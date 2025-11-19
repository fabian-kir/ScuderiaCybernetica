from hardware.robot_hub import RobotHub
from hardware.color_sensor import ColorSensor
from hardware.ultrasonic_sensor import UltrasonicSensor
from hardware.plattform_motors import PlattformMotors
from config.constants import CONSTANTS

from utils.data_logger import log_data

from hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        # Initialize sensors and motors
        self.color_sensor = ColorSensor()
        self.ultrasonic_sensor = UltrasonicSensor()
        self.drive_motor = DriveMotor()
        self.plattform_motors = PlattformMotors()

    def update(self, dt):
        self.control_x(dt)
        #self.control_y(dt)

    def control_x(self, dt):
        error = self.color_sensor.get_reflection_error() # this is already the relative error because the calibration in the beginning ensures it
        scaled_error = error * CONSTANTS.PLATFORM_X_KP

        self.plattform_motors.run_forever_x(scaled_error)
        RobotHub().print("speed:", scaled_error)

    def control_y(self, dt):
        return # TODO
        '''
        control y from motor resistance
        '''

        resistance = self.drive_motor.get_resistance()
        # correction_angle = resistance * CONSTANTS.PLATFORM_Y_KP #TODO !!! this won*'t work without calibration


        '''
        if correction_angle < CONSTANTS.BALANCE_X_ERROR_DEADBAND:
            correction_angle = 0.0
            log_data("correction_angle", correction_angle)
            return
        ''' # Deadbanding might be unnecessary, needs testing with the now introduced "track_target" command in platfform_motors. Was initially introduced to counter motor wiggle.

        self.plattform_motors.move_x(correction_angle)
        log_data("correction_angle", correction_angle)


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
