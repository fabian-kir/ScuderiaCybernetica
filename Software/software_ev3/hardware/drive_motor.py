import warnings

from pybricks.robotics import DriveBase

from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor
from pybricks.tools import wait

from controllers.controller import Controller
from hardware_wrapper import HardwareWrapper

class DriveMotor(HardwareWrapper):
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]

        print("Setting up drive motor on port:", self.port)
        self.motor = Motor(self.port)

        self.target_speed = 0
        self.power = 0
        self.power_per_speed = CONSTANTS["POWER_PER_SPEED"]

    def update(self, dt):
        speed = self.motor.speed()
        speed_error = self.target_speed - speed

        power_correction = speed_error * self.power_per_speed
        self.power += power_correction

        self.motor.dc(self.power)

    def drive(self, speed, slope=0):
        self.target_speed = speed

    def stop(self, brake_motors=True, hold_after=True):
        self.target_speed = 0

        if brake_motors:
            self.motor.dc( -self.power )
            wait(5)
            self.motor.dc(0)

        if hold_after:
            while True:
                if self.motor.speed() == 0:
                    break
            self.motor.hold()