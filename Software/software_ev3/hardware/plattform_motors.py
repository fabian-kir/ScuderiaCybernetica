from config.ports import PORTS
from pybricks.ev3devices import Motor

from utils.singleton import singleton
from config.constants import CONSTANTS

from Software.software_ev3.config import constants
from hardware.robot_hub import RobotHub


@singleton
class BalanceMotors:
    def __init__(self):
        self.port_x = PORTS["SMALL_BALANCE_MOTOR"]
        self.port_y = PORTS["LARGE_BALANCE_MOTOR"]

        self.gear_ratio_x = CONSTANTS["GEAR_RATIO_BALANCE_X"]
        self.gear_ratio_y = CONSTANTS["GEAR_RATIO_BALANCE_Y"]

        self.motor_x = Motor(self.port_x)
        self.motor_y = Motor(self.port_y)

        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)
        self.motor_x.hold()
        self.motor_y.hold()

        RobotHub().print("Set up balance motors x and y on ports:", self.port_x, self.port_y)

    def update(self, dt):
        pass

    def move_plattform(self, angle_x, angle_y):
        self.motor_x.run(angle_x * self.gear_ratio_x)
        self.motor_y.run(angle_y * self.gear_ratio_y)

    def hold(self):
        self.motor_x.hold()
        self.motor_y.hold()