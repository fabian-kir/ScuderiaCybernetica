import os

from software_ev3.utils.singleton import singleton
from software_ev3.utils.data_logger import log_data

from software_ev3.hardware.platform_motors import PlatformMotors
from software_ev3.hardware.robot_hub import RobotHub
from software_ev3.hardware.drive_motor import DriveMotor
from software_ev3.hardware.ultrasonic_sensor import UltrasonicSensor
from software_ev3.hardware.color_sensor import ColorSensor
from software_ev3.hardware.touch_sensors import TouchSensors

from software_ev3.controllers.platform_controller import PlatformController

from software_ev3.config.constants import CONSTANTS

from pybricks.tools import StopWatch, wait

@singleton
class Controller:
    """Main controller coordinating robot behavior."""
    def __init__(self):
        # HARDWARE WRAPPERS
        self.hub = RobotHub()
        self.plattform_motors = PlatformMotors()
        self.drive_motor = DriveMotor()
        self.ultrasonic_sensor = UltrasonicSensor()
        self.color_sensor = ColorSensor()
        self.touch_sensors = TouchSensors()

        # CONTROLLERS
        self.plattform_controller = PlatformController()

        self.to_update = [self.hub, self.touch_sensors, self.plattform_motors, self.drive_motor, self.color_sensor, self.ultrasonic_sensor, self.plattform_controller]
        self.running = False
        self.load_calibrations()

    def run(self):
        """Main control loop with delta timing using Pybricks StopWatch."""
        
        # Values for testing
        self.drive_motor.drive(0)

        # Main Loop
        self.running = True
        sw = StopWatch()          # starts at 0 ms
        last_ms = sw.time()       # initial timestamp

        while self.running:
            now_ms = sw.time()
            dt = (now_ms - last_ms) / 1000.0  # convert to seconds
            last_ms = now_ms

            if dt < .001:
                RobotHub().print("WARNING: dt is too small:", dt, "adjusting to .001")
                dt = .001

            self.update(dt)
            log_data("dt", dt)


    def load_calibrations(self):
        from software_ev3.utils.calibration_data import calibration_data

        if CONSTANTS.CALIBRATE_ON_START:
            hub = RobotHub()
            hub.await_user_confirmation("Set Plattform even, set motor on a flat road, then press middle button to calibrate.")

            self.color_sensor.save_calibration()
            self.ultrasonic_sensor.save_calibration()

        self.color_sensor.load_calibration()
        self.ultrasonic_sensor.load_calibration()

    def update(self, dt: float):
        for component in self.to_update:
            component.update(dt)
