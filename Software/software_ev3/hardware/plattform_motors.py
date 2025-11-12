from config.ports import PORTS
from pybricks.ev3devices import Motor
from pybricks.parameters import Stop

from utils.singleton import singleton
from config.constants import CONSTANTS

from hardware.robot_hub import RobotHub


@singleton
class PlattformMotors:
    def __init__(self):
        self.port_x = PORTS["SMALL_BALANCE_MOTOR"]
        self.port_y = PORTS["LARGE_BALANCE_MOTOR"]

        self.gear_ratio_x = CONSTANTS["GEAR_RATIO_BALANCE_X"]
        self.gear_ratio_y = CONSTANTS["GEAR_RATIO_BALANCE_Y"]

        self.motor_x = Motor(self.port_x)
        self.motor_y = Motor(self.port_y)

        self.default_speed_motor_x = CONSTANTS["DEFAULT_SPEED_BALANCE_X"]
        self.default_speed_motor_y = CONSTANTS["DEFAULT_SPEED_BALANCE_Y"]

        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)

        self.motor_x.hold()
        self.motor_y.hold()

        RobotHub().print("Set up balance motors x and y on ports:", self.port_x, self.port_y)

    def update(self, dt):
        _ = self.motor_x.angle() # TODO remove, it updates the emulator

    def move_plattform(self, d_angle_x=None, d_angle_y=None, speed_x=None, speed_y=None):
        assert d_angle_x is not None or d_angle_y is not None

        if speed_x is None:
            speed_x = self.default_speed_motor_x

        if speed_y is None:
            speed_y = self.default_speed_motor_y

        if d_angle_x is not None:
            self.motor_x.run_angle(speed_x, d_angle_x * self.gear_ratio_x, then=Stop.HOLD, wait=False)

        if d_angle_y is not None:
            self.motor_y.run_angle(speed_y, d_angle_y * self.gear_ratio_y, then=Stop.HOLD, wait=False)

    def hold(self):
        self.motor_x.hold()
        self.motor_y.hold()