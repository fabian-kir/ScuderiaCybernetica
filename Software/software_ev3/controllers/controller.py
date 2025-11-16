import os

from utils.singleton import singleton

from hardware.plattform_motors import PlattformMotors
from hardware.robot_hub import RobotHub
from hardware.drive_motor import DriveMotor
from hardware.ultrasonic_sensor import UltrasonicSensor
from hardware.color_sensor import ColorSensor

from controllers.plattform_controller import PlattformController

from pybricks.tools import StopWatch, wait
import time

# Import UI event processor for emulator mode
if os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES"):
    try:
        from pybricks.ui import process_ui_events
    except ImportError:
        process_ui_events = None
else:
    process_ui_events = None

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
        
        # Values for testing
        self.drive_motor.drive(0)

        # Main Loop
        self.running = True
        sw = StopWatch()          # starts at 0 ms
        last_ms = sw.time()       # initial timestamp

        try:
            while self.running:
                now_ms = sw.time()
                dt = (now_ms - last_ms) / 1000.0  # convert to seconds
                last_ms = now_ms

                if dt < .001:
                    RobotHub().print("WARNING: dt is too small:", dt, "adjusting to .001")
                    dt = .001

                self.update(dt)
                
                # Small sleep to prevent excessive CPU usage and allow UI to process
                time.sleep(0.001)  # 1ms sleep

        except KeyboardInterrupt:
            self.stop()

    def update(self, dt: float):
        """Periodic update logic."""
        # Process UI events for emulator (if enabled)
        if process_ui_events:
            try:
                process_ui_events()
            except Exception:
                pass  # Ignore errors if window is closed
        
        for component in self.to_update:
            component.update(dt)

    def stop(self):
        """Stop all motors safely."""
        self.running = False
        # TODO: Add graceful stop behavior
