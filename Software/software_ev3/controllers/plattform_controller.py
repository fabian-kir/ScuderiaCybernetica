from hardware.robot_hub import RobotHub
from hardware.color_sensor import ColorSensor
from hardware.ultrasonic_sensor import UltrasonicSensor
from hardware.plattform_motors import PlattformMotors
from config.constants import CONSTANTS


class PlattformController:
    def __init__(self):
        # Initialize sensors and motors
        self.color_sensor = ColorSensor()
        self.ultrasonic_sensor = UltrasonicSensor()
        self.plattform_motors = PlattformMotors()
        
        # Initialize PID state for color sensor (X-axis)
        self.color_integral = 0.0
        self.color_previous_error = 0.0
        
        # Initialize PID state for ultrasonic sensor (Y-axis)
        self.ultrasonic_integral = 0.0
        self.ultrasonic_previous_error = 0.0
        
        # Run calibration (will reset PID state)
        self.run_calibration()

    def update(self, dt):
        self.pid_from_color_sensor(dt)
        #self.pid_from_ultrasonic_sensor(dt)

    def pid_from_color_sensor(self, dt):
        """
        PID controller for platform balance using color sensor (X-axis).
        
        Maintains platform level by keeping reflection error at zero.
        Uses PID control with speed and angle limits to ensure smooth,
        reactive corrections without imparting impulse to objects on platform.
        
        Args:
            dt: Time delta in seconds since last update
        """
        # Get current error (positive when platform needs to tilt to correct)
        error = self.color_sensor.get_reflection_error()
        
        # Proportional term: immediate response to current error
        p_term = CONSTANTS["PLATFORM_COLOR_KP"] * error
        
        # Integral term: accumulates error over time to eliminate steady-state error
        # Prevents integral windup by clamping the accumulated value
        '''self.color_integral += error * dt
        max_integral = CONSTANTS["PLATFORM_MAX_INTEGRAL_X"]
        self.color_integral = max(-max_integral, min(max_integral, self.color_integral))
        i_term = CONSTANTS["PLATFORM_COLOR_KI"] * self.color_integral
        
        # Derivative term: responds to rate of change of error (dampens oscillations)
        error_rate = (error - self.color_previous_error) / dt if dt > 0 else 0.0
        d_term = CONSTANTS["PLATFORM_COLOR_KD"] * error_rate
        self.color_previous_error = error'''
        
        # Calculate total angle correction
        angle_correction = p_term #+ i_term + d_term
        
        # Limit angle correction per update to prevent sudden movements
        max_correction = CONSTANTS["PLATFORM_MAX_ANGLE_CORRECTION_X"]
        #angle_correction = max(-max_correction, min(max_correction, angle_correction))
        
        # Only move if correction is significant (avoid jitter from noise)
        if abs(angle_correction) > 0.1:
            # Limit speed to prevent impulse
            max_speed = CONSTANTS["PLATFORM_MAX_SPEED_X"]
            self.plattform_motors.move_plattform(
                d_angle_x=angle_correction,
                speed_x=max_speed
            )
    '''
    def pid_from_ultrasonic_sensor(self, dt):
        """
        PID controller for platform balance using ultrasonic sensor (Y-axis).
        
        Maintains platform level by keeping distance error at zero.
        Uses PID control with speed and angle limits to ensure smooth,
        reactive corrections without imparting impulse to objects on platform.
        
        Args:
            dt: Time delta in seconds since last update
        """
        # Get current error (positive when platform needs to tilt to correct)
        error = self.ultrasonic_sensor.get_distance_error()
        
        # Proportional term: immediate response to current error
        p_term = CONSTANTS["PLATFORM_ULTRASONIC_KP"] * error
        
        # Integral term: accumulates error over time to eliminate steady-state error
        # Prevents integral windup by clamping the accumulated value
        self.ultrasonic_integral += error * dt
        max_integral = CONSTANTS["PLATFORM_MAX_INTEGRAL_Y"]
        self.ultrasonic_integral = max(-max_integral, min(max_integral, self.ultrasonic_integral))
        i_term = CONSTANTS["PLATFORM_ULTRASONIC_KI"] * self.ultrasonic_integral
        
        # Derivative term: responds to rate of change of error (dampens oscillations)
        error_rate = (error - self.ultrasonic_previous_error) / dt if dt > 0 else 0.0
        d_term = CONSTANTS["PLATFORM_ULTRASONIC_KD"] * error_rate
        self.ultrasonic_previous_error = error
        
        # Calculate total angle correction
        angle_correction = p_term + i_term + d_term
        
        # Limit angle correction per update to prevent sudden movements
        max_correction = CONSTANTS["PLATFORM_MAX_ANGLE_CORRECTION_Y"]
        angle_correction = max(-max_correction, min(max_correction, angle_correction))
        
        # Only move if correction is significant (avoid jitter from noise)
        if abs(angle_correction) > 0.1:
            # Limit speed to prevent impulse
            max_speed = CONSTANTS["PLATFORM_MAX_SPEED_Y"]
            self.plattform_motors.move_plattform(
                d_angle_y=angle_correction,
                speed_y=max_speed
            )
    '''
    def run_calibration(self):
        hub = RobotHub()
        hub.await_user_confirmation("Set Plattform even, then press middle button to calibrate.")

        self.color_sensor.calibrate_to_current_state()
        self.ultrasonic_sensor.calibrate_to_current_state()
        
        # Reset PID state after calibration to start fresh
        self.color_integral = 0.0
        self.color_previous_error = 0.0
        self.ultrasonic_integral = 0.0
        self.ultrasonic_previous_error = 0.0
