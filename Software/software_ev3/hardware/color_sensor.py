from config.ports import PORTS
from pybricks.ev3devices import ColorSensor as PybricksColorSensor

from utils.singleton import singleton
from utils.data_logger import log_data
from hardware.robot_hub import RobotHub

@singleton
class ColorSensor:
    def __init__(self):
        self.port = PORTS["COLOR_SENSOR"]
        self.sensor = PybricksColorSensor(self.port)

        self.target_reflection = 0

        RobotHub().print("Set up color sensor on port:", self.port)

    def update(self, dt):
        log_data("color_sensor", self.sensor.reflection())

    def get_reflection_error(self):
        """Returns the difference between the current reflection and the target."""
        return self.target_reflection - self.sensor.reflection()

    def get_absolute_reflection(self):
        return self.sensor.reflection()

    def calibrate_to_current_state(self):
        self.target_reflection = self.get_absolute_reflection()

        RobotHub().print("Calibrated color sensor to current state.")