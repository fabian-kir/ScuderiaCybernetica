from utils.singleton import singleton

from hardware.plattform_motors import PlattformMotors
from hardware.robot_hub import RobotHub
from hardware.drive_motor import DriveMotor
from hardware.ultrasonic_sensor import UltrasonicSensor
from hardware.color_sensor import ColorSensor

from controllers.plattform_controller import PlattformController

from pybricks.tools import StopWatch, wait

@singleton
class Controller:
    """Main controller coordinating robot behavior."""
    def __init__(self):
        self.hub = RobotHub()
        self.plattform_motors = PlattformMotors()
        self.drive_motor = DriveMotor()
        self.ultrasonic_sensor = UltrasonicSensor()
        self.color_sensor = ColorSensor()

        self.plattform_controller = PlattformController()

        self.to_update = [self.hub, self.plattform_motors, self.drive_motor, self.ultrasonic_sensor, self.color_sensor, self.plattform_controller]

        self.running = False

    def run(self):
        """Main control loop with delta timing using Pybricks StopWatch."""
        RobotHub().play_startup_sound()

        # Values for testing
        self.drive_motor.drive(500)

        # Main Loop
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
