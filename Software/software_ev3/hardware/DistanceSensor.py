from config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor

class DistanceSensor:
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            return cls._instance

        # Creating a new instance
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        print("Setting up distance sensor on port:", port)
        self.sensor = UltrasonicSensor(self.port)