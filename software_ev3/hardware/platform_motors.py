from software_ev3.config.ports import PORTS
from pybricks.ev3devices import Motor

from software_ev3.utils.data_logger import log_data
from software_ev3.utils.singleton import singleton

from software_ev3.config.constants import CONSTANTS

from software_ev3.hardware.robot_hub import RobotHub

from software_ev3.exceptions import MotorControlException


@singleton
class PlatformMotors:
    """
    Controller for the balance platform motors (X and Y axes).
    
    Manages two motors that control the platform's tilt in X and Y directions.
    Supports independent movement of each axis with configurable gear ratios
    and default speeds.
    """
    
    def __init__(self):
        """Initialize platform motors with configuration from constants."""
        self.port_forward = PORTS["LARGE_BALANCE_MOTOR"]
        self.port_sideways = PORTS["SMALL_BALANCE_MOTOR"]

        self.motor_forward = Motor(self.port_forward, gears=[CONSTANTS.GEAR_RATIO_PLATFORM_FORWARD, ])
        self.motor_sideways = Motor(self.port_sideways, gears=[CONSTANTS.GEAR_RATIO_PLATFORM_SIDEWAYS, ])

        self.motor_forward.reset_angle(0)
        self.motor_sideways.reset_angle(0)

        RobotHub().print("Set up balance motors x and y on ports:", self.port_forward, self.port_sideways)

    def update(self, dt):
        log_data("balance_motor_x", self.motor_forward.angle())
        log_data("balance_motor_y", self.motor_sideways.angle())

    def forward_track_target(self, angle):
        if angle > CONSTANTS.MOTOR_FORWARD_MAX_DEGREE:
            angle = CONSTANTS.MOTOR_FORWARD_MAX_DEGREE # this could raise an exception, but without one is better to ensure we continue working
        elif angle < -CONSTANTS.MOTOR_FORWARD_MAX_DEGREE:
            angle = -CONSTANTS.MOTOR_FORWARD_MAX_DEGREE

        self.motor_forward.track_target(angle * CONSTANTS.GEAR_RATIO_BALANCE_FORWARD)

    def sideways_track_target(self, angle):
        if angle > CONSTANTS.MOTOR_SIDEWAYS_MAX_DEGREE:
            angle = CONSTANTS.MOTOR_SIDEWAYS_MAX_DEGREE
        elif angle < -CONSTANTS.MOTOR_SIDEWAYS_MAX_DEGREE:
            angle = -CONSTANTS.MOTOR_SIDEWAYS_MAX_DEGREE

        self.motor_sideways.track_target(angle * CONSTANTS.GEAR_RATIO_BALANCE_SIDEWAYS)

    def forward_set_speed(self, speed):
        if abs(speed) < CONSTANTS.MIN_SPEED_PLATFORM_FORWARD:
            raise MotorControlException("Motor speed is lower than minimum speed. This leads to motor wiggle. Set speed: " + speed)

        if speed > 0 and self.forward_get_angle() > CONSTANTS.MOTOR_FORWARD_MAX_ANGLE:
            speed = 0
        elif speed < 0 and self.forward_get_angle() < -CONSTANTS.MOTOR_FORWARD_MAX_ANGLE:
            speed = 0

        self.motor_forward.run(speed)

    def sideways_set_speed(self, speed):
        if abs(speed) < CONSTANTS.MIN_SPEED_PLATFORM_SIDEWAYS:
            raise MotorControlException("Motor speed is lower than minimum speed. This leads to motor wiggle. Set speed: " + speed)

        if speed > 0 and self.sideways_get_angle() > CONSTANTS.MOTOR_FORWARD_MAX_ANGLE:
            speed = 0
        elif speed < 0 and self.sideways_get_angle() < -CONSTANTS.MOTOR_FORWARD_MAX_ANGLE:
            speed = 0

        self.motor_sideways.run(speed)

    def hold(self):
        """
        Hold both motors at their current positions.
        
        Prevents the platform from moving when no active command is running.
        """
        self.motor_forward.hold()
        self.motor_sideways.hold()
    
    def forward_get_angle(self):
        return self.motor_forward.angle() / CONSTANTS.GEAR_RATIO_BALANCE_X
    
    def sideways_get_angle(self):
        return self.motor_sideways.angle() / CONSTANTS.GEAR_RATIO_BALANCE_Y
        