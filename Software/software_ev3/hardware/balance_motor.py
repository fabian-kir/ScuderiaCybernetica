from config.ports import PORTS
from pybricks.ev3devices import Motor

from utils.singleton import singleton


@singleton
class BalanceMotors:
    def __init__(self):
        print("Setting up Balance Motors")
        pass

    def update(self, dt):
        print("TODO")
