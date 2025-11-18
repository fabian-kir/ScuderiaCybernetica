from config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor as PybricksUltrasonicSensor
from pybricks.ev3devices import InfraredSensor

from utils.singleton import singleton
from utils.data_logger import log_data
from hardware.robot_hub import RobotHub


@singleton
class UltrasonicSensor:
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        # self.sensor = PybricksUltrasonicSensor(self.port)
        self.sensor = InfraredSensor(self.port) # This will cause an error ! remove line and uncomment the one above!

        self.target_distance = 0.0

        RobotHub().print("Set up ultrasonic sensor on port:", self.port)

    def calibrate_to_current_state(self):
        from utils.calibration_data import calibration_data

        self.target_distance = self.get_absolute_distance()
        calibration_data.ultrasound_sensor_target_distance = self.target_distance
        RobotHub().print("Calibrated ultrasonic sensor to current state.")

    def update(self, dt):
        log_data("ultrasonic_sensor", self.sensor.distance())

    def get_distance_error(self):
        """Returns the difference between the current distance and the target."""
        return self.target_distance - self.sensor.distance()

    def get_absolute_distance(self):
        return self.sensor.distance()

    def load_calibration_data(self):
        from utils.calibration_data import calibration_data

        self.target_distance = calibration_data.ultrasound_sensor_target_distance
        RobotHub().print("loaded ultrasonic target distance to:", self.target_distance)
