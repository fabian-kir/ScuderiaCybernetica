from utils.singleton import singleton

# from .plattform_controller import PlattformController
from hardware.plattform_motors import PlattformMotors
from hardware.distance_sensor import DistanceSensor
from hardware.robot_hub import RobotHub
from hardware.slope_sensor import SlopeSensor
from pybricks.tools import StopWatch, wait

from controllers.plattform_controller import PlattformController

@singleton
class Controller:
    """Main controller coordinating robot behavior."""
    def __init__(self):
        self.hub = RobotHub()
        self.plattform_motors = PlattformMotors()
        self.slope_sensor = SlopeSensor()
        self.distance_sensor = DistanceSensor()
        self.plattform_controller = PlattformController()

        self.to_update = [self.hub, self.plattform_motors, self.slope_sensor, self.distance_sensor, self.plattform_controller]

        self.running = False

    def run(self):
        """Main control loop with delta timing using Pybricks StopWatch."""

        self.plattform_motors.move_plattform(180, 180)

        self.running = True
        sw = StopWatch()          # starts at 0 ms
        last_ms = sw.time()       # initial timestamp

        try:
            while self.running:
                now_ms = sw.time()
                dt = (now_ms - last_ms) / 1000.0  # convert to seconds
                last_ms = now_ms

                self.update(dt)

        except KeyboardInterrupt:
            self.stop()

    def update(self, dt: float):
        """Periodic update logic."""
        for component in self.to_update:
            component.update(dt)

    def stop(self):
        """Stop all motors safely."""
        self.running = False
        # TODO: Add graceful stop behavior
