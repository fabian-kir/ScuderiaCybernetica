"""
Pybricks ev3devices module emulation

Provides Motor and Sensor classes for the EV3.
"""

import time
from typing import List, Optional
from ..emulator_state import emulator_state, MotorMode
from .parameters import Port, Stop, Direction, Color


class Motor:
    """
    EV3 Motor
    
    Controls a single motor connected to the EV3.
    Supports various control modes: dc, run, run_time, run_angle, run_target, track_target.
    """
    
    def __init__(self, port, positive_direction=Direction.CLOCKWISE, gears: Optional[List[float]] = None):
        """
        Initialize a motor
        
        Args:
            port: Port to which the motor is connected
            positive_direction: Direction considered positive
            gears: Optional gear train ratios
        """
        self.port = str(port)
        self.positive_direction = positive_direction
        self.gears = gears or [1.0]
        
        # Register with emulator state
        emulator_state.register_motor(self.port, self.gears)
        
        emulator_state.log_event(f"Motor initialized on port {self.port}")
    
    def _get_gear_ratio(self) -> float:
        """Get the total gear ratio"""
        ratio = 1.0
        for gear in self.gears:
            ratio *= gear
        return ratio
    
    def angle(self) -> float:
        """
        Get the rotation angle of the motor
        
        Returns:
            Angle in degrees
        """
        motor = emulator_state.get_motor(self.port)
        if motor:
            return motor['angle'] / self._get_gear_ratio()
        return 0.0
    
    def speed(self) -> float:
        """
        Get the speed of the motor
        
        This operation takes 50ms as specified.
        
        Returns:
            Speed in degrees per second
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.motor_speed_delay)
        
        motor = emulator_state.get_motor(self.port)
        if motor:
            return motor['speed'] / self._get_gear_ratio()
        return 0.0
    
    def reset_angle(self, angle: float = 0):
        """
        Reset the motor angle to a specific value
        
        Args:
            angle: New angle value in degrees
        """
        gear_ratio = self._get_gear_ratio()
        emulator_state.update_motor(self.port, angle=angle * gear_ratio)
    
    def stop(self):
        """
        Stop the motor and let it coast
        """
        emulator_state.set_motor_mode(self.port, MotorMode.STOP, 0)
    
    def brake(self):
        """
        Passively resist movement (brake)
        """
        emulator_state.set_motor_mode(self.port, MotorMode.STOP, 0)
    
    def hold(self):
        """
        Stop the motor and actively hold position
        """
        emulator_state.set_motor_mode(self.port, MotorMode.HOLD, 0)
    
    def run(self, speed: float):
        """
        Run the motor at a constant speed
        
        Args:
            speed: Target speed in degrees per second
        """
        gear_ratio = self._get_gear_ratio()
        adjusted_speed = speed * gear_ratio
        emulator_state.set_motor_mode(self.port, MotorMode.RUN, adjusted_speed)
        emulator_state.update_motor(self.port, target_speed=adjusted_speed)
    
    def run_time(self, speed: float, time_ms: int, then: Stop = Stop.HOLD, wait: bool = True):
        """
        Run the motor at a constant speed for a specific time
        
        Args:
            speed: Target speed in degrees per second
            time_ms: Duration in milliseconds
            then: What to do after time expires
            wait: Whether to wait for completion
        """
        gear_ratio = self._get_gear_ratio()
        adjusted_speed = speed * gear_ratio
        
        emulator_state.set_motor_mode(self.port, MotorMode.RUN_TIME, adjusted_speed)
        emulator_state.update_motor(self.port, target_speed=adjusted_speed)
        
        if wait:
            time.sleep(time_ms / 1000.0)
            if then == Stop.HOLD:
                self.hold()
            elif then == Stop.BRAKE:
                self.brake()
            else:
                self.stop()
    
    def run_angle(self, speed: float, rotation_angle: float, then: Stop = Stop.HOLD, wait: bool = True):
        """
        Run the motor at a constant speed for a specific angle
        
        Args:
            speed: Target speed in degrees per second
            rotation_angle: Angle to rotate in degrees
            then: What to do after rotation completes
            wait: Whether to wait for completion
        """
        gear_ratio = self._get_gear_ratio()
        adjusted_speed = speed * gear_ratio
        adjusted_angle = rotation_angle * gear_ratio
        
        current_angle = emulator_state.get_motor(self.port)['angle']
        target_angle = current_angle + adjusted_angle
        
        emulator_state.set_motor_mode(self.port, MotorMode.RUN_ANGLE, adjusted_speed)
        emulator_state.update_motor(self.port, target_speed=adjusted_speed, target_angle=target_angle)
        
        if wait:
            # Estimate time needed
            time_needed = abs(rotation_angle / speed)
            time.sleep(time_needed)
            
            # Update angle
            emulator_state.update_motor(self.port, angle=target_angle)
            
            if then == Stop.HOLD:
                self.hold()
            elif then == Stop.BRAKE:
                self.brake()
            else:
                self.stop()
    
    def run_target(self, speed: float, target_angle: float, then: Stop = Stop.HOLD, wait: bool = True):
        """
        Run the motor to an absolute target angle
        
        Args:
            speed: Maximum speed in degrees per second
            target_angle: Target angle in degrees
            then: What to do after reaching target
            wait: Whether to wait for completion
        """
        gear_ratio = self._get_gear_ratio()
        adjusted_speed = speed * gear_ratio
        adjusted_target = target_angle * gear_ratio
        
        current_angle = emulator_state.get_motor(self.port)['angle']
        angle_diff = abs(adjusted_target - current_angle)
        
        emulator_state.set_motor_mode(self.port, MotorMode.RUN_TARGET, adjusted_speed)
        emulator_state.update_motor(self.port, target_speed=adjusted_speed, target_angle=adjusted_target)
        
        if wait:
            # Estimate time needed
            time_needed = angle_diff / adjusted_speed
            time.sleep(time_needed)
            
            # Update angle
            emulator_state.update_motor(self.port, angle=adjusted_target)
            
            if then == Stop.HOLD:
                self.hold()
            elif then == Stop.BRAKE:
                self.brake()
            else:
                self.stop()
    
    def track_target(self, target_angle: float):
        """
        Track a target angle (for smooth following of changing targets)
        
        Args:
            target_angle: Target angle in degrees
        """
        gear_ratio = self._get_gear_ratio()
        adjusted_target = target_angle * gear_ratio
        
        emulator_state.set_motor_mode(self.port, MotorMode.TRACK_TARGET, adjusted_target)
        emulator_state.update_motor(self.port, target_angle=adjusted_target)
    
    def dc(self, duty: float):
        """
        Set motor duty cycle (direct power control)
        
        This is the low-level control mode where you set the duty cycle directly.
        The motor speed is not regulated and depends on the load.
        
        Args:
            duty: Duty cycle from -100 to 100 (percentage)
        """
        emulator_state.set_motor_mode(self.port, MotorMode.DC, duty)
        emulator_state.update_motor(self.port, dc_value=duty)
    
    def run_until_stalled(self, speed: float, then: Stop = Stop.HOLD, duty_limit: Optional[float] = None):
        """
        Run the motor until it stalls
        
        Args:
            speed: Target speed
            then: What to do after stall
            duty_limit: Duty cycle limit
        
        Returns:
            Angle at which the motor stalled
        """
        # Simplified for emulator - just run for a short time
        self.run(speed)
        time.sleep(0.5)
        
        if then == Stop.HOLD:
            self.hold()
        elif then == Stop.BRAKE:
            self.brake()
        else:
            self.stop()
        
        return self.angle()
    
    def stalled(self) -> bool:
        """Check if the motor is currently stalled"""
        motor = emulator_state.get_motor(self.port)
        if motor:
            return motor.get('stall_detected', False)
        return False
    
    def load(self) -> float:
        """
        Get the load on the motor
        
        Returns:
            Estimated load as a percentage
        """
        # Simplified for emulator
        return 50.0


class ColorSensor:
    """
    EV3 Color Sensor
    
    Detects colors and measures reflected light intensity.
    """
    
    def __init__(self, port):
        """
        Initialize the color sensor
        
        Args:
            port: Port to which the sensor is connected
        """
        self.port = str(port)
        emulator_state.register_sensor(self.port, "ColorSensor")
        emulator_state.log_event(f"ColorSensor initialized on port {self.port}")
    
    def color(self) -> Optional[Color]:
        """
        Get the detected color
        
        Returns:
            Color enum value or None
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        # Map reflection to color (simplified)
        reflection = emulator_state.get_sensor_value(self.port)
        
        if reflection < 10:
            return Color.BLACK
        elif reflection < 25:
            return Color.BLUE
        elif reflection < 40:
            return Color.GREEN
        elif reflection < 55:
            return Color.YELLOW
        elif reflection < 70:
            return Color.RED
        elif reflection < 85:
            return Color.WHITE
        else:
            return Color.WHITE
    
    def reflection(self) -> int:
        """
        Get the reflection intensity
        
        Returns:
            Reflection percentage (0-100)
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return int(value) if value is not None else 0
    
    def ambient(self) -> int:
        """
        Get ambient light intensity
        
        Returns:
            Ambient light percentage (0-100)
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        # Similar to reflection for simplicity
        value = emulator_state.get_sensor_value(self.port)
        return int(value * 0.8) if value is not None else 0
    
    def rgb(self) -> tuple:
        """
        Get RGB color values
        
        Returns:
            Tuple of (red, green, blue) percentages
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        # Simplified: return based on reflection
        reflection = emulator_state.get_sensor_value(self.port)
        return (reflection, reflection, reflection)


class UltrasonicSensor:
    """
    EV3 Ultrasonic Sensor
    
    Measures distance to objects using ultrasonic sound waves.
    """
    
    def __init__(self, port):
        """
        Initialize the ultrasonic sensor
        
        Args:
            port: Port to which the sensor is connected
        """
        self.port = str(port)
        emulator_state.register_sensor(self.port, "UltrasonicSensor")
        emulator_state.log_event(f"UltrasonicSensor initialized on port {self.port}")
    
    def distance(self) -> int:
        """
        Get the distance to the nearest object
        
        Returns:
            Distance in millimeters
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return int(value) if value is not None else 2550
    
    def presence(self) -> bool:
        """
        Check if any object is detected
        
        Returns:
            True if an object is detected, False otherwise
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        distance = emulator_state.get_sensor_value(self.port)
        return distance is not None and distance < 2550


class TouchSensor:
    """
    EV3 Touch Sensor
    
    Detects when the sensor button is pressed.
    """
    
    def __init__(self, port):
        """
        Initialize the touch sensor
        
        Args:
            port: Port to which the sensor is connected
        """
        self.port = str(port)
        emulator_state.register_sensor(self.port, "TouchSensor")
        emulator_state.log_event(f"TouchSensor initialized on port {self.port}")
    
    def pressed(self) -> bool:
        """
        Check if the sensor is pressed
        
        Returns:
            True if pressed, False otherwise
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return bool(value) if value is not None else False


class GyroSensor:
    """
    EV3 Gyro Sensor
    
    Measures rotation rate and angle.
    """
    
    def __init__(self, port, direction=Direction.CLOCKWISE):
        """
        Initialize the gyro sensor
        
        Args:
            port: Port to which the sensor is connected
            direction: Positive direction
        """
        self.port = str(port)
        self.direction = direction
        emulator_state.register_sensor(self.port, "GyroSensor")
        emulator_state.log_event(f"GyroSensor initialized on port {self.port}")
    
    def speed(self) -> int:
        """
        Get the rotation rate
        
        Returns:
            Rotation rate in degrees per second
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return int(value) if value is not None else 0
    
    def angle(self) -> int:
        """
        Get the accumulated angle
        
        Returns:
            Angle in degrees
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return int(value) if value is not None else 0
    
    def reset_angle(self, angle: int = 0):
        """Reset the angle to a specific value"""
        emulator_state.set_sensor_value(self.port, angle)


class InfraredSensor:
    """
    EV3 Infrared Sensor
    
    Measures distance and detects infrared beacons.
    """
    
    def __init__(self, port):
        """
        Initialize the infrared sensor
        
        Args:
            port: Port to which the sensor is connected
        """
        self.port = str(port)
        emulator_state.register_sensor(self.port, "InfraredSensor")
        emulator_state.log_event(f"InfraredSensor initialized on port {self.port}")
    
    def distance(self) -> int:
        """
        Get approximate distance to an object
        
        Returns:
            Distance percentage (0-100)
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        value = emulator_state.get_sensor_value(self.port)
        return int(value) if value is not None else 100
    
    def beacon(self, channel: int) -> tuple:
        """
        Get beacon location
        
        Returns:
            Tuple of (distance, angle) or (None, None) if not detected
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        return (None, None)
    
    def buttons(self, channel: int) -> list:
        """
        Get pressed buttons on the infrared remote
        
        Returns:
            List of pressed buttons
        """
        # Simulate 50ms delay
        time.sleep(emulator_state.sensor_read_delay)
        
        return []

