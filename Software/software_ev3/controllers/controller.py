from utils.singleton import singleton

# from .plattform_controller import PlattformController
from hardware.balance_motor import BalanceMotors
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
        self.balance_motor = BalanceMotors()
        self.slope_sensor = SlopeSensor()
        self.distance_sensor = DistanceSensor()
        self.plattform_controller = PlattformController()

        self.to_update = [self.hub, self.balance_motor, self.slope_sensor, self.distance_sensor, self.plattform_controller]

        self.running = False

    def run(self):
        """Main control loop with delta timing using Pybricks StopWatch."""

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
