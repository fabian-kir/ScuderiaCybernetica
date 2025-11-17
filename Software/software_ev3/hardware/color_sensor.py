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

        self._last_reflections = []

    def update(self, dt):
        log_data("color_sensor", self.sensor.reflection())
        self._last_reflections.append(self.get_absolute_reflection())

    def get_reflection_error(self, smoothed_for_iterations=5):
        """
        Returns the difference between the current reflection and the target.
        """

        # smoothing the output so it's averaged across the last iterations in order to get less jiggle in the motor
        current_reflection = self.sensor.reflection()
        if smoothed_for_iterations > 0 and len(self._last_reflections) >= smoothed_for_iterations:
            current_reflection = int(sum(self._last_reflections[:smoothed_for_iterations]) / smoothed_for_iterations)

        return self.target_reflection - self.sensor.reflection()

    def get_absolute_reflection(self):
        return self.sensor.reflection()

    def calibrate_to_current_state(self):
        from utils.calibration_data import calibration_data

        self.target_reflection = self.get_absolute_reflection()
        calibration_data.color_sensor_target_reflection = self.target_reflection
        RobotHub().print("Calibrated color sensor to current state.")

    def load_calibration_data(self):
        from utils.calibration_data import calibration_data

        self.target_reflection = calibration_data.color_sensor_target_reflection