from config.ports import PORTS
from pybricks.ev3devices import Motor
from pybricks.parameters import Stop

from utils.singleton import singleton
from config.constants import CONSTANTS

from hardware.robot_hub import RobotHub


@singleton
class PlattformMotors:
    """
    Controller for the balance platform motors (X and Y axes).
    
    Manages two motors that control the platform's tilt in X and Y directions.
    Supports independent movement of each axis with configurable gear ratios
    and default speeds.
    """
    
    def __init__(self):
        """Initialize platform motors with configuration from constants."""
        self.port_x = PORTS["SMALL_BALANCE_MOTOR"]
        self.port_y = PORTS["LARGE_BALANCE_MOTOR"]

        # Gear ratios applied to angle commands
        # actual_motor_angle = command_angle * gear_ratio
        self.gear_ratio_x = CONSTANTS["GEAR_RATIO_BALANCE_X"]
        self.gear_ratio_y = CONSTANTS["GEAR_RATIO_BALANCE_Y"]

        self.motor_x = Motor(self.port_x)
        self.motor_y = Motor(self.port_y)

        # Default speeds used when speed is not explicitly specified
        self.default_speed_motor_x = CONSTANTS["DEFAULT_SPEED_BALANCE_X"]
        self.default_speed_motor_y = CONSTANTS["DEFAULT_SPEED_BALANCE_Y"]

        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)

        self.motor_x.hold()
        self.motor_y.hold()

        RobotHub().print("Set up balance motors x and y on ports:", self.port_x, self.port_y)

    def update(self, dt):
        """
        Periodic update method called by the main controller loop.
        
        Args:
            dt: Time delta in seconds since last update
        """

    def move_x(self, d_angle, spee: int = None):
        if speed is None:
            speed = self.default_speed_motor_x
        
        self.motor_x.run_angle(speed, d_angle, then=Stop.HOLD, wait=False)

    def move_y(self, d_angle, speed: int = None):
        if speed is None:
            speed = self.default_speed_motor_y
        
        self.motor_y.run_angle(speed, d_angle, then=Stop.HOLD, wait=False)

    def hold(self):
        """
        Hold both motors at their current positions.
        
        Prevents the platform from moving when no active command is running.
        """
        self.motor_x.hold()
        self.motor_y.hold()

    def get_angles(self):
        return self.motor_x.angle(), self.motor_y.angle()