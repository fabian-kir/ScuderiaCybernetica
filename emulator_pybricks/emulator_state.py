"""
Emulator State Management

Centralized state for all motors, sensors, and hub components.
Manages the UI and coordinates communication between mocked pybricks objects and the UI.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class MotorMode(Enum):
    """Motor control modes"""
    IDLE = "idle"
    DC = "dc"
    RUN = "run"
    RUN_TIME = "run_time"
    RUN_ANGLE = "run_angle"
    RUN_TARGET = "run_target"
    TRACK_TARGET = "track_target"
    HOLD = "hold"
    STOP = "stop"


class EmulatorState:
    """
    Singleton state manager for the emulator.
    
    Manages all motor and sensor states, button presses, and UI events.
    Thread-safe for use with both the robot code and UI threads.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._state_lock = threading.Lock()
        
        # Motors state: {port: motor_info}
        self.motors: Dict[str, Dict[str, Any]] = {}
        
        # Sensors state: {port: sensor_info}
        self.sensors: Dict[str, Dict[str, Any]] = {}
        
        # Hub state
        self.hub_state = {
            'battery_voltage': 8000,  # mV
            'button_led_color': None,
            'buttons_pressed': set(),
            'screen_lines': [],
            'speaker_events': []
        }
        
        # Console output buffer
        self.console_buffer: List[str] = []
        
        # UI update callback
        self.ui_update_callback: Optional[Callable] = None
        
        # Timing simulation
        self.sensor_read_delay = 0.05  # 50ms
        self.motor_speed_delay = 0.05  # 50ms
    
    def register_ui_callback(self, callback: Callable):
        """Register a callback for UI updates"""
        with self._state_lock:
            self.ui_update_callback = callback
    
    def notify_ui_update(self):
        """Notify UI that state has changed"""
        if self.ui_update_callback:
            try:
                self.ui_update_callback()
            except Exception as e:
                print(f"Error in UI update callback: {e}")
    
    # Motor management
    def register_motor(self, port: str, gears: List[float] = None):
        """Register a motor on a specific port"""
        with self._state_lock:
            if port not in self.motors:
                self.motors[port] = {
                    'port': port,
                    'mode': MotorMode.IDLE,
                    'angle': 0.0,
                    'speed': 0.0,
                    'dc_value': 0.0,
                    'target_speed': 0.0,
                    'target_angle': 0.0,
                    'gears': gears or [1.0],
                    'control_value': 0.0,  # The current control value (power, speed, etc.)
                    'stall_detected': False
                }
                self.log_event(f"Motor registered on {port}")
                self.notify_ui_update()
    
    def update_motor(self, port: str, **kwargs):
        """Update motor state"""
        with self._state_lock:
            if port in self.motors:
                self.motors[port].update(kwargs)
                self.notify_ui_update()
    
    def get_motor(self, port: str) -> Optional[Dict[str, Any]]:
        """Get motor state"""
        with self._state_lock:
            return self.motors.get(port, None)
    
    def set_motor_mode(self, port: str, mode: MotorMode, control_value: float = 0.0):
        """Set motor mode and control value"""
        with self._state_lock:
            if port in self.motors:
                old_mode = self.motors[port]['mode']
                self.motors[port]['mode'] = mode
                self.motors[port]['control_value'] = control_value
                
                if mode == MotorMode.DC:
                    self.motors[port]['dc_value'] = control_value
                elif mode == MotorMode.RUN:
                    self.motors[port]['target_speed'] = control_value
                elif mode == MotorMode.HOLD:
                    self.motors[port]['target_speed'] = 0
                    self.motors[port]['speed'] = 0
                
                self.log_event(f"Motor {port}: {old_mode.value} -> {mode.value} (value: {control_value})")
                self.notify_ui_update()
    
    def simulate_motor_physics(self, dt: float):
        """Simulate motor physics (speed changes based on mode)"""
        with self._state_lock:
            for port, motor in self.motors.items():
                mode = motor['mode']
                
                if mode == MotorMode.DC:
                    # In DC mode, speed depends on the DC value and load
                    # Simulate: speed approaches dc_value * max_speed
                    target_speed = motor['dc_value'] * 1000  # Approximate max speed
                    motor['speed'] = motor['speed'] * 0.9 + target_speed * 0.1
                    motor['angle'] += motor['speed'] * dt
                    
                elif mode == MotorMode.RUN:
                    # In RUN mode, speed quickly approaches target
                    motor['speed'] = motor['speed'] * 0.8 + motor['target_speed'] * 0.2
                    motor['angle'] += motor['speed'] * dt
                    
                elif mode == MotorMode.HOLD:
                    motor['speed'] = 0
                    
                elif mode == MotorMode.TRACK_TARGET:
                    # Move towards target angle
                    angle_diff = motor['target_angle'] - motor['angle']
                    if abs(angle_diff) > 1:
                        speed_needed = angle_diff * 5  # Proportional control
                        motor['speed'] = max(-1000, min(1000, speed_needed))
                        motor['angle'] += motor['speed'] * dt
                    else:
                        motor['speed'] = 0
                
                elif mode in [MotorMode.IDLE, MotorMode.STOP]:
                    motor['speed'] *= 0.95  # Slow decay
                    motor['angle'] += motor['speed'] * dt
    
    # Sensor management
    def register_sensor(self, port: str, sensor_type: str):
        """Register a sensor on a specific port"""
        with self._state_lock:
            if port not in self.sensors:
                default_value = 0
                if sensor_type == "ColorSensor":
                    default_value = 50  # reflection percentage
                elif sensor_type == "UltrasonicSensor":
                    default_value = 100  # mm
                elif sensor_type == "TouchSensor":
                    default_value = False
                
                self.sensors[port] = {
                    'port': port,
                    'type': sensor_type,
                    'value': default_value
                }
                self.log_event(f"{sensor_type} registered on {port}")
                self.notify_ui_update()
    
    def set_sensor_value(self, port: str, value: Any):
        """Set sensor value (from UI)"""
        with self._state_lock:
            if port in self.sensors:
                self.sensors[port]['value'] = value
                self.notify_ui_update()
    
    def get_sensor_value(self, port: str) -> Any:
        """Get sensor value (with simulated delay)"""
        time.sleep(self.sensor_read_delay)
        with self._state_lock:
            if port in self.sensors:
                return self.sensors[port]['value']
            return None
    
    # Hub button management
    def press_button(self, button: str):
        """Simulate button press"""
        with self._state_lock:
            self.hub_state['buttons_pressed'].add(button)
            self.log_event(f"Button pressed: {button}")
            self.notify_ui_update()
    
    def release_button(self, button: str):
        """Simulate button release"""
        with self._state_lock:
            self.hub_state['buttons_pressed'].discard(button)
            self.log_event(f"Button released: {button}")
            self.notify_ui_update()
    
    def get_pressed_buttons(self) -> set:
        """Get currently pressed buttons"""
        with self._state_lock:
            return self.hub_state['buttons_pressed'].copy()
    
    # Hub screen management
    def screen_print(self, *args):
        """Add text to screen"""
        with self._state_lock:
            text = ' '.join(str(arg) for arg in args)
            self.hub_state['screen_lines'].append(text)
            # Keep only last 20 lines
            if len(self.hub_state['screen_lines']) > 20:
                self.hub_state['screen_lines'].pop(0)
            self.log_console(f"SCREEN: {text}")
            self.notify_ui_update()
    
    def screen_clear(self):
        """Clear screen"""
        with self._state_lock:
            self.hub_state['screen_lines'].clear()
            self.notify_ui_update()
    
    # Speaker management
    def play_sound(self, sound_name: str):
        """Log sound event"""
        self.log_event(f"🔊 Sound: {sound_name}")
    
    def beep(self, frequency: int = 500, duration: int = 100):
        """Log beep event"""
        self.log_event(f"🔊 Beep: {frequency}Hz for {duration}ms")
    
    # LED management
    def set_button_led(self, color):
        """Set button LED color"""
        with self._state_lock:
            self.hub_state['button_led_color'] = color
            self.log_event(f"💡 LED: {color}")
            self.notify_ui_update()
    
    # Console logging
    def log_console(self, message: str):
        """Add message to console"""
        timestamp = time.strftime("%H:%M:%S")
        with self._state_lock:
            self.console_buffer.append(f"[{timestamp}] {message}")
            # Keep only last 100 messages
            if len(self.console_buffer) > 100:
                self.console_buffer.pop(0)
            self.notify_ui_update()
    
    def log_event(self, message: str):
        """Log an event (different from console print)"""
        timestamp = time.strftime("%H:%M:%S")
        with self._state_lock:
            self.console_buffer.append(f"[{timestamp}] {message}")
            if len(self.console_buffer) > 100:
                self.console_buffer.pop(0)
            self.notify_ui_update()
    
    def get_console_text(self) -> str:
        """Get all console text"""
        with self._state_lock:
            return '\n'.join(self.console_buffer)
    
    def get_battery_voltage(self) -> int:
        """Get battery voltage in mV"""
        with self._state_lock:
            return self.hub_state['battery_voltage']
    
    def set_battery_voltage(self, voltage: int):
        """Set battery voltage"""
        with self._state_lock:
            self.hub_state['battery_voltage'] = voltage
            self.notify_ui_update()


# Global emulator state instance
emulator_state = EmulatorState()

