import warnings

from pybricks.robotics import DriveBase

from ..config.ports import PORTS
from ..config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from ..controllers.controller import Controller
from hardware_wrapper import HardwareWrapper


class PowerTrain(HardwareWrapper):
    def __init__(self):
        self.port_left = PORTS["LEFT_MOTOR"]
        self.port_right = PORTS["RIGHT_MOTOR"]

        print("Setting up left motor on port:", self.port_left)
        self.left = Motor(self.port_left)

        print("Setting up right motor on port:", self.port_right)
        self.right = Motor(self.port_right)

        print("Setting up drive base")
        self.drive_base = DriveBase(self.left, self.right, wheel_diameter=CONSTANTS["WHEEL_DIAMETER"], axle_track=CONSTANTS["AXLE_TRACK"])

        self.time_intervalls = [] # update intervalls
        self.distances = [] # distance travelled for each update intervall. WARNING: Not adjusted for turns or slopes
        self.turn_angles = [] # angle turned for each update intervall

        self.default_speed = CONSTANTS["DEFAULT_SPEED"]

    def update(self, dt):
        self.time_intervalls.append(dt)
        self.distances.append(self.drive_base.distance())
        self.turn_angles.append(self.drive_base.angle())
        self.drive_base.reset()

    def drive(self, speed=None, turn_rate=0.0, slope=0.0):
        # TODO adjust speed for slope: We should decide: Would we want to have the robot drive faster as slope increases, so that the
        #      speed along the floor-plane stays constant, so we do not introduce any swings on the plattform?

        if speed is None:
            speed = self.default_speed
        self.drive_base.drive(speed, turn_rate)

    def get_absolute_distance(self):
        return sum(self.distances) + self.drive_base.distance()

    def travelled_since_last_update(self): # in mm
        return self.distances[-1]

    def stop(self):
        self.drive_base.stop()