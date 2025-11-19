from hardware.robot_hub import RobotHub
from hardware.color_sensor import ColorSensor
from hardware.plattform_motors import PlattformMotors
from config.constants import CONSTANTS

from utils.data_logger import log_data

from hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        # Initialize sensors and motors
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.plattform_motors = PlattformMotors()

    def update(self, dt):
        self.control_x(dt)
        self.control_y(dt)

    def control_x(self, dt):
        error = self.color_sensor.get_reflection_error() # this is already the relative error because the calibration in the beginning ensures it
        scaled_error = error * CONSTANTS.PLATFORM_X_KP

        self.plattform_motors.run_forever_x(scaled_error)

    def control_y(self, dt):
    def pid_from_ultrasonic_sensor(self, dt):
        error = self.drive_motor.get_slope_angle()
        scaled_error = error * CONSTANTS.PLATFORM_Y_KP

        self.plattform_motors.run_forever_y(scaled_error)

