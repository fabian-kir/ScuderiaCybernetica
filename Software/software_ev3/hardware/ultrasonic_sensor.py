from config.ports import PORTS
from pybricks.ev3devices import UltrasonicSensor as PybricksUltrasonicSensor

from utils.singleton import singleton
from hardware.robot_hub import RobotHub


@singleton
class UltrasonicSensor:
    def __init__(self):
        self.port = PORTS["ULTRASONIC_SENSOR"]
        self.sensor = PybricksUltrasonicSensor(self.port)

        self.target_distance = 0.0

        RobotHub().print("Set up ultrasonic sensor on port:", self.port)

    def calibrate_to_current_state(self):
        self.target_distance = self.get_distance()
        RobotHub().print("Calibrated ultrasonic sensor to current state.")

    def update(self, dt):
        pass

    def get_distance_error(self):
        """Returns the difference between the current distance and the target."""
        return self.target_distance - self.sensor.distance()

    def get_absolute_distance(self):
        return self.sensor.distance()