from config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor

from utils.singleton import singleton
from hardware.robot_hub import RobotHub


@singleton
class UltrasonicSensor:
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        self.sensor = UltrasonicSensor(self.port)

        RobotHub().print("Set up ultrasonic sensor on port:", self.port)

    def update(self, dt):
        # TODO
        RobotHub().print("Ultrasonic sensor update not implemented yet")