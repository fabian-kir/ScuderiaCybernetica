from __future__ import annotations

import threading
import time
import traceback
import uuid
from collections import deque
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple

SENSOR_READ_LATENCY = 0.05  # seconds
_CONSOLE_MAX_ENTRIES = 500


@dataclass
class MotorState:
    """Serializable snapshot of a motor."""

    id: str
    port: str
    name: str
    mode: str = "idle"
    command: float = 0.0
    actual_speed: float = 0.0
    feedback_speed: float = 0.0
    angle: float = 0.0

    def snapshot(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SensorState:
    """Serializable snapshot of a sensor."""

    id: str
    port: str
    name: str
    sensor_type: str
    value: Any = 0
    meta: Dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConsoleEvent:
    seq: int
    timestamp: float
    level: str
    message: str

    def snapshot(self) -> Dict[str, Any]:
        return asdict(self)


class EmulatorRuntime:
    """Global coordination point for the desktop Pybricks emulator."""

    def __init__(self):
        self._lock = threading.RLock()
        self._motors: Dict[str, Dict[str, Any]] = {}
        self._sensors: Dict[str, SensorState] = {}
        self._buttons: Dict[str, Any] = {}
        self._console: Deque[ConsoleEvent] = deque(maxlen=_CONSOLE_MAX_ENTRIES)
        self._console_seq = 0
        self._start_time = time.time()
        self._shutdown = threading.Event()
        self._robot_thread: Optional[threading.Thread] = None
        self._robot_done = threading.Event()
        self._ui_thread_id: Optional[int] = None
        self._battery_voltage_mv = 7400

    # --------------------------------------------------------------------- #
    # Motor handling
    # --------------------------------------------------------------------- #
    def register_motor(self, motor_obj: Any, port: Any, name: str) -> str:
        motor_id = str(uuid.uuid4())
        port_name = getattr(port, "name", str(port))
        state = MotorState(id=motor_id, port=port_name, name=name)
        with self._lock:
            self._motors[motor_id] = {"motor": motor_obj, "state": state}
        self.append_console(f"Registered motor {name} on port {port_name}", level="debug")
        return motor_id

    def update_motor_state(
        self,
        motor_id: str,
        *,
        mode: Optional[str] = None,
        command: Optional[float] = None,
        actual_speed: Optional[float] = None,
        feedback_speed: Optional[float] = None,
        angle: Optional[float] = None,
    ) -> None:
        with self._lock:
            entry = self._motors.get(motor_id)
            if not entry:
                return
            state: MotorState = entry["state"]
            if mode is not None:
                state.mode = mode
            if command is not None:
                state.command = command
            if actual_speed is not None:
                state.actual_speed = actual_speed
            if feedback_speed is not None:
                state.feedback_speed = feedback_speed
            if angle is not None:
                state.angle = angle

    def set_motor_feedback(self, motor_id: str, speed: float) -> None:
        motor = None
        with self._lock:
            entry = self._motors.get(motor_id)
            if entry:
                motor = entry["motor"]
        if motor is not None:
            motor.set_feedback_speed(speed)

    def snapshot_motors(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [entry["state"].snapshot() for entry in self._motors.values()]

    # --------------------------------------------------------------------- #
    # Sensor handling
    # --------------------------------------------------------------------- #
    def register_sensor(
        self,
        *,
        name: str,
        port: Any,
        sensor_type: str,
        initial_value: Any,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        sensor_id = str(uuid.uuid4())
        port_name = getattr(port, "name", str(port))
        state = SensorState(
            id=sensor_id,
            port=port_name,
            name=name,
            sensor_type=sensor_type,
            value=initial_value,
            meta=meta or {},
        )
        with self._lock:
            self._sensors[sensor_id] = state
        self.append_console(f"Registered sensor {name} on port {port_name}", level="debug")
        return sensor_id

    def read_sensor_value(self, sensor_id: str) -> Any:
        with self._lock:
            state = self._sensors.get(sensor_id)
            if not state:
                raise KeyError(f"Unknown sensor id {sensor_id}")
            return state.value

    def set_sensor_value(self, sensor_id: str, value: Any) -> None:
        with self._lock:
            state = self._sensors.get(sensor_id)
            if not state:
                return
            state.value = value

    def snapshot_sensors(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [state.snapshot() for state in self._sensors.values()]

    # --------------------------------------------------------------------- #
    # Buttons & battery
    # --------------------------------------------------------------------- #
    def set_button_state(self, button: Any, pressed: bool) -> None:
        name = getattr(button, "name", str(button))
        with self._lock:
            if pressed:
                self._buttons[name] = button
            else:
                self._buttons.pop(name, None)

    def get_pressed_buttons(self) -> Tuple[Any, ...]:
        with self._lock:
            return tuple(self._buttons.values())

    def set_battery_voltage_mv(self, voltage_mv: int) -> None:
        with self._lock:
            self._battery_voltage_mv = int(voltage_mv)

    def get_battery_voltage_mv(self) -> int:
        with self._lock:
            return self._battery_voltage_mv

    # --------------------------------------------------------------------- #
    # Console events
    # --------------------------------------------------------------------- #
    def append_console(self, message: str, level: str = "info") -> None:
        with self._lock:
            self._console_seq += 1
            event = ConsoleEvent(
                seq=self._console_seq,
                timestamp=time.time() - self._start_time,
                level=level,
                message=message,
            )
            self._console.append(event)

    def consume_console_events(self, last_seq: int) -> Tuple[List[Dict[str, Any]], int]:
        with self._lock:
            events = [event.snapshot() for event in self._console if event.seq > last_seq]
            new_seq = self._console_seq
        return events, new_seq

    # --------------------------------------------------------------------- #
    # UI lifecycle helpers
    # --------------------------------------------------------------------- #
    def process_ui_events(self) -> None:
        # Called from robot thread while waiting for UI interaction.
        time.sleep(0.005)

    def launch(self, robot_entrypoint: Callable[[], None]) -> None:
        from emulator_pybricks.ui.app import EmulatorApp

        if self._ui_thread_id is not None:
            raise RuntimeError("Emulator already running")

        def robot_runner():
            try:
                robot_entrypoint()
            except Exception as exc:  # pragma: no cover - debugging helper
                tb = traceback.format_exc()
                self.append_console(f"Robot thread crashed: {exc}", level="error")
                self.append_console(tb, level="debug")
            finally:
                self._robot_done.set()

        self._robot_done.clear()
        self._robot_thread = threading.Thread(
            target=robot_runner,
            name="EV3RobotThread",
            daemon=True,
        )
        self._robot_thread.start()

        app = EmulatorApp(self)
        self._ui_thread_id = threading.get_ident()
        try:
            app.run()
        finally:
            self.request_shutdown()
            if self._robot_thread and self._robot_thread.is_alive():
                self._robot_thread.join(timeout=0.5)

    def is_robot_running(self) -> bool:
        return bool(self._robot_thread and self._robot_thread.is_alive())

    def request_shutdown(self) -> None:
        self._shutdown.set()

    def should_shutdown(self) -> bool:
        return self._shutdown.is_set()


_RUNTIME: Optional[EmulatorRuntime] = None
_RUNTIME_LOCK = threading.Lock()


def get_runtime() -> EmulatorRuntime:
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is None:
            _RUNTIME = EmulatorRuntime()
        return _RUNTIME


def launch_emulator(robot_entrypoint: Callable[[], None]) -> None:
    runtime = get_runtime()
    runtime.launch(robot_entrypoint)


def simulate_sensor_latency() -> None:
    time.sleep(SENSOR_READ_LATENCY)

