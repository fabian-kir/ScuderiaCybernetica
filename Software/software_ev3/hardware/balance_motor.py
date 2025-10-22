from ..config.ports import PORTS
from pybricks.ev3devices import Motor

from hardware_wrapper import HardwareWrapper


class BalanceMotor(HardwareWrapper):
    def __init__(self):
        self.port = PORTS["BALANCE_MOTOR"]
        print("Setting up balance motor on port:", self.port)
        self.motor = Motor(self.port)

    def move_to(self, angle):
        # TODO

    def stop(self):
        """Stop balancing."""
        self.motor.stop()
