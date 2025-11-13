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
        _ = self.motor_x.angle()  # TODO: remove, it updates the emulator

    def move_plattform(self, d_angle_x=None, d_angle_y=None, speed_x=None, speed_y=None):
        """
        Move the platform by specified angles on X and/or Y axes.
        
        At least one axis (d_angle_x or d_angle_y) must be specified.
        If speed is not provided for an axis, the default speed is used.
        Gear ratios are automatically applied to angle commands.
        
        Args:
            d_angle_x: Desired angle change in degrees for X-axis (optional)
            d_angle_y: Desired angle change in degrees for Y-axis (optional)
            speed_x: Speed in deg/s for X-axis movement (optional, uses default if None)
            speed_y: Speed in deg/s for Y-axis movement (optional, uses default if None)
        
        Raises:
            AssertionError: If both d_angle_x and d_angle_y are None
        """
        assert d_angle_x is not None or d_angle_y is not None, \
            "At least one axis (d_angle_x or d_angle_y) must be specified"

        if speed_x is None:
            speed_x = self.default_speed_motor_x

        if speed_y is None:
            speed_y = self.default_speed_motor_y

        if d_angle_x is not None:
            # Apply gear ratio: motor rotates by d_angle_x * gear_ratio_x
            self.motor_x.run_angle(speed_x, d_angle_x * self.gear_ratio_x, then=Stop.HOLD, wait=False)

        if d_angle_y is not None:
            # Apply gear ratio: motor rotates by d_angle_y * gear_ratio_y
            self.motor_y.run_angle(speed_y, d_angle_y * self.gear_ratio_y, then=Stop.HOLD, wait=False)

    def hold(self):
        """
        Hold both motors at their current positions.
        
        Prevents the platform from moving when no active command is running.
        """
        self.motor_x.hold()
        self.motor_y.hold()