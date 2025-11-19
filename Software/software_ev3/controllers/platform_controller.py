from hardware.robot_hub import RobotHub
from hardware.color_sensor import ColorSensor
from hardware.plattform_motors import PlattformMotors
from hardware.touch_sensors import TouchSensors
from config.constants import CONSTANTS

from utils.data_logger import log_data

from hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        # Initialize sensors and motors
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.plattform_motors = PlattformMotors()

        self.time_since_beginning = 0
        self.time_until_controller_starts = 1
        self.controller_has_started = False

    def update(self, dt):
        if not self.time_since_beginning + dt > self.time_until_controller_starts:
            self.time_since_beginning += dt
            return
        
        elif not self.controller_has_started:
            RobotHub().beep()
            self.controller_has_started = True

        self.control_x(dt)
        self.control_y(dt)

    def control_x(self, dt):
        error = self.color_sensor.get_reflection_error() # this is already the relative error because the calibration in the beginning ensures it
        scaled_error = error * CONSTANTS.PLATFORM_X_KP

        log_data("balance_motor_x_speed", scaled_error)
        self.plattform_motors.run_forever_x(scaled_error)

    def control_y(self, dt):
        slope_angle = self.drive_motor.get_slope_angle()
        motor_angle = self.plattform_motors.get_angle_y()

        log_data("slope_angle", slope_angle)
        log_data("motor_angle", motor_angle)
        
        self.plattform_motors.move_y(slope_angle)

        #log_data("y-speed", error * CONSTANTS.PLATFORM_Y_KP)
        #self.plattform_motors.run_forever_y(error * CONSTANTS.PLATFORM_Y_KP)
        #self.plattform_motors.track_target_y(slope_angle, 11, 0, 0)

