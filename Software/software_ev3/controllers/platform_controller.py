from hardware.robot_hub import RobotHub
from hardware.color_sensor import ColorSensor
from hardware.plattform_motors import PlattformMotors
from hardware.touch_sensors import TouchSensors
from hardware.ultrasonic_sensor import UltrasonicSensor
from config.constants import CONSTANTS

from utils.data_logger import log_data

from hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        # Initialize sensors and motors
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.plattform_motors = PlattformMotors()
        self.touch_sensors = TouchSensors()
        self.ultrasonic_sensor = UltrasonicSensor()

        self.time_since_beginning = 0
        self.time_until_controller_starts = 1
        self.controller_has_started = False

        self.wall_hit_delay = 0

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
        soll_ultrasonic = CONSTANTS.PLATFORM_Y_ULTRASONIC_KP * self.ultrasonic_sensor.get_distance_error()
        soll_drive_motor = self.drive_motor.get_slope_angle()

        avg_soll = (soll_ultrasonic + soll_drive_motor) / 2

        log_data("avg_soll", avg_soll)

        if self.touch_sensors.is_any_pressed():
            avg_soll = soll_ultrasonic

        ist = self.plattform_motors.get_angle_y()

        #soll = self.drive_motor.get_slope_angle()
        #ist = self.plattform_motors.get_angle_y()

        #log_data("drive_motor_detected_angle", soll)
        log_data("small_balance_motor_angle", ist)

        self.plattform_motors.run_forever_y( (avg_soll-ist)*CONSTANTS.PLATFORM_Y_ULTRASONIC_SPEED_KP)

    def control_y_through_ultrasonic(self, dt):
        soll = CONSTANTS.PLATFORM_Y_ULTRASONIC_KP * self.ultrasonic_sensor.get_distance_error() # this is already the relative error because the calibration in the beginning ensures it
        ist = self.plattform_motors.get_angle_y()

        #self.plattform_motors.move_y(scaled_error * CONSTANTS.PLATFORM_Y_ULTRASONIC_KP)

        log_data("ultrasonic_detected_angle", soll)
        self.plattform_motors.run_forever_y( (soll-ist)*CONSTANTS.PLATFORM_Y_ULTRASONIC_SPEED_KP )
