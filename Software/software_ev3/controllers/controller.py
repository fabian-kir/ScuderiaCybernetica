from utils.singleton import singleton

# from .plattform_controller import PlattformController
from hardware.balance_motor import BalanceMotors
from hardware.distance_sensor import DistanceSensor
from hardware.robot_hub import RobotHub
from hardware.slope_sensor import SlopeSensor
from pybricks.tools import StopWatch

@singleton
class Controller:
    """Main controller coordinating robot behavior."""
    def __init__(self):
        self.update_handlers= []

        self.hub = RobotHub()
        self.balance_motor = BalanceMotors()
        self.slope_sensor = SlopeSensor()
        self.distance_sensor = DistanceSensor()

        # self.plattform_controller = PlattformController()

        self.running = False

    def register_update_handler(self, handler: callable):
        """Register a function to be called on every update.
        THIS SHOULD ONLY EVER BE USED BY CHILDREN OF HARDWAREWRAPPER!!!
        NO CONTROLLERS MAY USE THIS CLASS!!!"""
        self.update_handlers.append(handler)


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

        #IMPORTANT: First .update to anybody registered...
        for handler in self.update_handlers:
            handler(dt)

        #          ... then .control() to subcontrollers
        # self.plattform_controller.control(dt)

    def stop(self):
        """Stop all motors safely."""
        self.running = False
        # TODO: Add graceful stop behavior
