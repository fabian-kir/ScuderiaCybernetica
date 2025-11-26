from software_ev3.config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor as PybricksUltrasonicSensor

from software_ev3.utils.singleton import singleton
from software_ev3.utils.data_logger import log_data
from software_ev3.hardware.robot_hub import RobotHub


@singleton
class UltrasonicSensor:
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        self.sensor = PybricksUltrasonicSensor(self.port)

        self.last_stable_distance = 0
        self.target_distance = 0

        RobotHub().print("Set up ultrasonic sensor on port:", self.port)

    def save_calibration(self):
        from software_ev3.utils.calibration_data import calibration_data

        target_distance = 0

        for i in range(5):
            target_distance = self.get_distance()

            if target_distance > 0:
                self.target_distance = target_distance
                break

        else: # if the loop was not stopped by break
            raise Exception("Could not calibrate ultrasonic sensor.")

        calibration_data.set("ultrasonic_sensor_target_distance", self.target_distance)

        RobotHub().print("Calibrated ultrasonic sensor to current state.")

    def update(self, dt):
        log_data("ultrasonic_sensor_distance_error", self.get_distance_error())

    def get_distance_error(self):
        """Returns the difference between the current distance and the target."""
        return self.target_distance - self.get_distance()

    def get_distance(self):
        distance = self.sensor.distance()
        if distance > 1000:
            return self.last_stable_distance

        self.last_stable_distance = distance
        return distance

    def load_calibration(self):
        from software_ev3.utils.calibration_data import calibration_data

        self.target_distance = calibration_data.get("ultrasonic_sensor_target_distance")
        RobotHub().print("loaded ultrasonic sensor target distance to:", self.target_distance)