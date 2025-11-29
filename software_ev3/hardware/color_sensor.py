from software_ev3.config.ports import PORTS
from pybricks.ev3devices import ColorSensor as PybricksColorSensor

from software_ev3.utils.singleton import singleton
from software_ev3.utils.data_logger import log_data
from software_ev3.hardware.robot_hub import RobotHub

@singleton
class ColorSensor:
    def __init__(self):
        self.port = PORTS["COLOR_SENSOR"]
        self.sensor = PybricksColorSensor(self.port)

        self.target_reflection = 0

        RobotHub().print("Set up color sensor on port:", self.port)

    def update(self, dt):
        return
        #log_data("color_sensor", self.get_reflection_error())

    def get_reflection_error(self, smoothed_for_iterations=5):
        """
        Returns the difference between the current reflection and the target.
        """
        current_reflection = self.get_reflection()
        return self.target_reflection - current_reflection

    def get_reflection(self):
        return self.sensor.reflection()

    def save_calibration(self):
        from software_ev3.utils.calibration_data import calibration_data

        reflection = self.get_reflection()

        calibration_data.set("color_sensor_target_reflection", reflection)
        RobotHub().print("Calibrated color sensor to current state.")

    def load_calibration(self):
        from software_ev3.utils.calibration_data import calibration_data

        self.target_reflection = calibration_data.get("color_sensor_target_reflection")
        RobotHub().print("loaded color sensor target reflection to:", self.target_reflection)
