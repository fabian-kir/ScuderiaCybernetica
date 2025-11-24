from software_ev3.hardware.robot_hub import RobotHub
from software_ev3.hardware.color_sensor import ColorSensor
from software_ev3.hardware.platform_motors import PlatformMotors
from software_ev3.hardware.touch_sensors import TouchSensors
from software_ev3.hardware.ultrasonic_sensor import UltrasonicSensor
from software_ev3.config.constants import CONSTANTS
from pybricks.tools import StopWatch, wait

from software_ev3.utils.data_logger import log_data

from software_ev3.hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        self.hub = RobotHub()
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.platform_motors = PlatformMotors()
        self.touch_sensors = TouchSensors()
        self.ultrasonic_sensor = UltrasonicSensor()

        self.time_since_startup = 0

    def update(self, dt):
        if not self.controller_ready(dt):
            return

        self.sideways_proportional_speed_control(dt)
        self.forward_proportional_speed_control(dt)

    def sideways_proportional_speed_control(self, dt):
        error = self.color_sensor.get_reflection_error()
        self.platform_motors.sideways_set_speed(error * CONSTANTS.PLATFORM_SIDEWAYS_SPEED_KP)

    def forward_proportional_speed_control(self, dt):
        slope_soll = self.drive_motor.get_slope()
        slope_ist = self.platform_motors.forward_get_angle()
        error = slope_soll - slope_ist
        self.platform_motors.forward_set_speed(error * CONSTANTS.PLATFORM_FORWARD_SPEED_KP)

    def controller_ready(self, dt):
        self.time_since_startup += dt
        if self.time_since_startup >= CONSTANTS.TIME_UNTIL_PLATFORM_CONTROLLER_STARTS:
            return True
        return False

class PlatformController:
    def __init__(self):
        # Initialize sensors and motors
        self.hub = RobotHub()
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.plattform_motors = PlattformMotors()
        self.touch_sensors = TouchSensors()
        self.ultrasonic_sensor = UltrasonicSensor()

        self.time_since_beginning = 0
        self.time_until_controller_starts = 1
        self.controller_has_started = False
        self.watch = StopWatch()
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

        scaled_error = max(min(scaled_error, CONSTANTS.PLATFORM_X_MAX_SPEED), -CONSTANTS.PLATFORM_X_MAX_SPEED)
        self.plattform_motors.run_forever_x(scaled_error)

    def control_y(self, dt):
        soll_ultrasonic = CONSTANTS.PLATFORM_Y_ULTRASONIC_KP * self.ultrasonic_sensor.get_distance_error()
        soll_drive_motor = self.drive_motor.get_slope()

        avg_soll =  (soll_drive_motor + soll_ultrasonic)/2

        log_data("avg_soll", avg_soll)

        """
        if self.touch_sensors.is_any_pressed():
            self.watch.reset()
            # RobotHub().beep()
            avg_soll = soll_ultrasonic
        elif self.watch.time() < 2000:
            # RobotHub().beep()
            avg_soll = soll_ultrasonic
        """

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
