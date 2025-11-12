from config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor

from utils.singleton import singleton


@singleton
class DistanceSensor:
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        print("Setting up distance sensor on port:", self.port)
        self.sensor = UltrasonicSensor(self.port)

    def update(self, dt):
        print("TODO update distance sensor")