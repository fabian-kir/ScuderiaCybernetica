from config.ports import PORTS
from hardware.hardware_wrapper import HardwareWrapper
from pybricks.ev3devices import UltrasonicSensor

class DistanceSensor(HardwareWrapper):
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        print("Setting up distance sensor on port:", self.port)
        self.sensor = UltrasonicSensor(self.port)

    def update(dt):
        print("TODO update distance sensor")