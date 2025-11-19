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
        self.port_x = PORTS["LARGE_BALANCE_MOTOR"]
        self.port_y = PORTS["SMALL_BALANCE_MOTOR"]

        # Gear ratios applied to angle commands
        # actual_motor_angle = command_angle * gear_ratio
        self.gear_ratio_x = CONSTANTS.GEAR_RATIO_BALANCE_X
        self.gear_ratio_y = CONSTANTS.GEAR_RATIO_BALANCE_Y

        self.motor_x = Motor(self.port_x, gears=[self.gear_ratio_x, ])
        self.motor_y = Motor(self.port_y, gears=[self.gear_ratio_y, ])

        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)

        self.motor_x.hold()
        self.motor_y.hold()

        RobotHub().print("Set up balance motors x and y on ports:", self.port_x, self.port_y)

    def update(self, dt):
        if self.motor_x.angle() > CONSTANTS.MOTOR_X_MAX_DEGREE:
            self.motor_x.track_target(CONSTANTS.MOTOR_X_MAX_DEGREE)

        elif self.motor_x.angle() < -CONSTANTS.MOTOR_X_MAX_DEGREE:
            self.motor_x.track_target(-CONSTANTS.MOTOR_X_MAX_DEGREE)


        """
        Periodic update method called by the main controller loop.
        
        Args:
            dt: Time delta in seconds since last update
        """

    def move_x(self, angle):
        self.motor_x.track_target(angle * self.gear_ratio_x) # IMPORTANT: use track target, as it ensures no wiggle when small angle changes occur

    def move_y(self, angle):      
        return

    def run_forever_x(self, speed):
        self.motor_x.run(speed)

    def hold(self):
        """
        Hold both motors at their current positions.
        
        Prevents the platform from moving when no active command is running.
        """
        self.motor_x.hold()
        self.motor_y.hold()

    def get_angles(self):
        return self.motor_x.angle(), self.motor_y.angle()
    
    def get_angle_x(self):
        return self.motor_x.angle()
    
    def get_angle_y(self):
        return self.motor_x.angle()