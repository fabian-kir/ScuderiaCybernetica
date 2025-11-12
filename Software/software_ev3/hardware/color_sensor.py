from config.ports import PORTS
from pybricks.ev3devices import ColorSensor as PybricksColorSensor

from utils.singleton import singleton
from hardware.robot_hub import RobotHub


@singleton
class ColorSensor:
    def __init__(self):
        self.port = PORTS["COLOR_SENSOR"]
        self.sensor = PybricksColorSensor(self.port)

        RobotHub().print("Set up color sensor on port:", self.port)

    def update(self, dt):
        # TODO
        RobotHub().print("color sensor update not implemented yet")

    def get_reflection(self):
        return self.sensor.reflection()