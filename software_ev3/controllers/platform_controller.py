from software_ev3.hardware.robot_hub import RobotHub
from software_ev3.hardware.color_sensor import ColorSensor
from software_ev3.hardware.platform_motors import PlatformMotors
from software_ev3.hardware.ultrasonic_sensor import UltrasonicSensor
from software_ev3.config.constants import CONSTANTS
from pybricks.tools import StopWatch, wait
import math

from software_ev3.utils.data_logger import log_data

from software_ev3.hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        self.hub = RobotHub()
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.platform_motors = PlatformMotors()
        self.ultrasonic_sensor = UltrasonicSensor()

        self.time_since_startup = 0

    def update(self, dt):
        if not self.controller_ready(dt):
            return

        self.sideways_proportional_speed_control(dt)
        self.forward_mathematical_speed_control(dt)

    def sideways_proportional_speed_control(self, dt):
        error = self.color_sensor.get_reflection_error()

        self.platform_motors.sideways_set_speed(error * CONSTANTS.PLATFORM_SIDEWAYS_SPEED_KP,
                                                ramp_up_speed_to_min=True)

    def forward_proportional_speed_control(self, dt):
        slope_soll = self.ultrasonic_sensor.get_distance_error()        
        slope_ist = self.platform_motors.forward_get_angle()
        error = slope_soll - slope_ist
        self.platform_motors.forward_set_speed(error * CONSTANTS.PLATFORM_FORWARD_SPEED_KP,
                                               ramp_up_speed_to_min=True)
        
    def forward_mathematical_speed_control(self, dt):
        slope_soll = 360 * (math.asin(min(max(self.ultrasonic_sensor.get_distance_error() / CONSTANTS.ULTRASONIC_PENDULUM_LENGTH, -1), 1)) / 2*math.pi)
        slope_ist = self.platform_motors.forward_get_angle()

        error = slope_soll - slope_ist
        self.platform_motors.forward_set_speed(error * CONSTANTS.PLATFORM_FORWARD_SPEED_KP,
                                               ramp_up_speed_to_min=True)

    def controller_ready(self, dt):
        self.time_since_startup += dt
        if self.time_since_startup >= CONSTANTS.TIME_UNTIL_PLATFORM_CONTROLLER_STARTS:
            return True
        return False