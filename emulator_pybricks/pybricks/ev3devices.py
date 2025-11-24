from __future__ import annotations

import time
from typing import Iterable, Optional

from emulator_pybricks.runtime import get_runtime, simulate_sensor_latency
from pybricks.parameters import Stop

__all__ = ["Motor", "ColorSensor", "UltrasonicSensor", "TouchSensor"]


class Motor:
    """CPU-side approximation of the Pybricks Motor class."""

    def __init__(self, port, gears: Optional[Iterable[int]] = None, name: Optional[str] = None):
        self._runtime = get_runtime()
        self.port = port
        self.gears = list(gears) if gears else []
        self.name = name or f"Motor({getattr(port, 'name', port)})"

        self._mode = "idle"
        self._command_value = 0.0
        self._actual_speed = 0.0
        self._feedback_speed = 0.0
        self._angle = 0.0
        self._last_update = time.time()

        self._id = self._runtime.register_motor(self, port, self.name)

    # Basic motion ----------------------------------------------------- #
    def run(self, speed: float) -> None:
        self._update_kinematics()
        self._mode = "speed"
        self._command_value = float(speed)
        self._push_state()

    def dc(self, duty_cycle: float) -> None:
        self._update_kinematics()
        self._mode = "dc"
        self._command_value = float(duty_cycle)
        self._push_state()

    def stop(self) -> None:
        self._update_kinematics()
        self._mode = "stopped"
        self._command_value = 0.0
        self._push_state()

    def hold(self) -> None:
        self._update_kinematics()
        self._mode = "hold"
        self._command_value = 0.0
        self._push_state()

    def track_target(self, angle: float) -> None:
        self._update_kinematics()
        self._mode = "track"
        self._angle = float(angle)
        self._push_state()

    def run_time(self, speed: float, duration_ms: int, stop_type: Stop = Stop.COAST) -> None:
        """Simplified blocking run_time helper used mainly for tests."""
        self.run(speed)
        time.sleep(duration_ms / 1000.0)
        if stop_type == Stop.HOLD:
            self.hold()
        else:
            self.stop()

    # Feedback --------------------------------------------------------- #
    def angle(self) -> float:
        self._update_kinematics()
        return self._angle

    def reset_angle(self, angle: float = 0.0) -> None:
        self._update_kinematics()
        self._angle = float(angle)
        self._push_state()

    def speed(self) -> float:
        simulate_sensor_latency()
        self._update_kinematics()
        return self._actual_speed

    def set_feedback_speed(self, speed: float) -> None:
        self._feedback_speed = float(speed)
        self._update_kinematics()
        self._push_state()

    # Internal helpers ------------------------------------------------- #
    def _update_kinematics(self) -> None:
        now = time.time()
        dt = now - self._last_update
        self._last_update = now

        actual_speed = self._compute_actual_speed()
        self._angle += actual_speed * dt
        self._actual_speed = actual_speed

    def _compute_actual_speed(self) -> float:
        if self._mode == "speed":
            return self._command_value
        if self._mode == "dc":
            return self._feedback_speed
        return 0.0

    def _push_state(self) -> None:
        self._runtime.update_motor_state(
            self._id,
            mode=self._mode,
            command=self._command_value,
            actual_speed=self._actual_speed,
            feedback_speed=self._feedback_speed,
            angle=self._angle,
        )


class ColorSensor:
    def __init__(self, port, name: Optional[str] = None):
        runtime = get_runtime()
        self._runtime = runtime
        self.port = port
        self.name = name or f"ColorSensor({getattr(port, 'name', port)})"
        self._sensor_id = runtime.register_sensor(
            name=self.name,
            port=port,
            sensor_type="reflection",
            initial_value=50,
            meta={"control": "slider", "min": 0, "max": 100, "step": 1, "unit": "%"},
        )

    def reflection(self) -> float:
        simulate_sensor_latency()
        return float(self._runtime.read_sensor_value(self._sensor_id))


class UltrasonicSensor:
    def __init__(self, port, name: Optional[str] = None):
        runtime = get_runtime()
        self._runtime = runtime
        self.port = port
        self.name = name or f"Ultrasonic({getattr(port, 'name', port)})"
        self._sensor_id = runtime.register_sensor(
            name=self.name,
            port=port,
            sensor_type="distance_mm",
            initial_value=300,
            meta={"control": "slider", "min": 0, "max": 2000, "step": 5, "unit": "mm"},
        )

    def distance(self) -> float:
        simulate_sensor_latency()
        return float(self._runtime.read_sensor_value(self._sensor_id))


class TouchSensor:
    def __init__(self, port, name: Optional[str] = None):
        runtime = get_runtime()
        self._runtime = runtime
        self.port = port
        self.name = name or f"TouchSensor({getattr(port, 'name', port)})"
        self._sensor_id = runtime.register_sensor(
            name=self.name,
            port=port,
            sensor_type="touch",
            initial_value=False,
            meta={"control": "toggle"},
        )

    def pressed(self) -> bool:
        simulate_sensor_latency()
        return bool(self._runtime.read_sensor_value(self._sensor_id))

