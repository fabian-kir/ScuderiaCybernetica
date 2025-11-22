from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from hardware.robot_hub import RobotHub

from exceptions import MotorControlException

from utils.controllers import PIDController
from utils.singleton import singleton
from utils.data_logger import log_data
from utils.interpolation_from_array import Interpolation2DFromArray
from utils.csv_file_handler import CSVFileHandler


@singleton
class DriveMotor:
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port, gears=[CONSTANTS.GEAR_RATIO_DRIVE_MOTOR])
        self.motor.reset_angle(0)

        self.interpolation = None
        self.load_slope_calibration() # loads the calibration data from last calibration and creates interpolation

        self._power = 0

        self.pid_controller = PIDController(
            kp=CONSTANTS.DRIVE_MOTOR_KP,
            ki=CONSTANTS.DRIVE_MOTOR_KI,
            kd=CONSTANTS.DRIVE_MOTOR_KD,
            get_state=self.get_speed
        )

        # Target speed (deg/s)
        self.target_speed = CONSTANTS.DRIVE_MOTOR_TARGET_SPEED
        self.drive(self.target_speed)

    def stop(self):
        self.set_dc(0)
        self.motor.stop()
        self.target_speed = 0

    def get_speed(self):
        return self.motor.speed()

    def set_power(self, power):
        if power == 0:
            self._power = 0
            self.motor.hold()
            return
        
        elif 0 < abs(power) < CONSTANTS.DRIVE_MOTOR_MIN_POWER:
            raise MotorControlException("Drive Motor power is set to a power lower than DRIVE_MOTOR_MIN_POWER")
        
        elif 0 > abs(power) > -CONSTANTS.DRIVE_MOTOR_MIN_POWER:
            raise MotorControlException("Drive Motor power is set to a power lower than DRIVE_MOTOR_MIN_POWER")

        self._power = power
        self.motor.dc(self._power / RobotHub().get_battery_voltage())

    def get_power(self):
        return self._power

    def drive(self, speed):
        if speed == 0:
            self.motor.hold()

        if abs(speed) > CONSTANTS.DRIVE_MOTOR_MAX_SPEED:
            raise MotorControlException("Drive Motor speed is set to a speed higher than DRIVE_MOTOR_MAX_SPEED")

        log_data("target_speed", speed)
        self.target_speed = speed

    def update(self, dt):
        log_data("drive_motor_speed", self.motor.speed())
        log_data("drive_motor_power", self.get_power())
        log_data("target_speed", self.target_speed)

        # PID Control Speed:
        power = self.pid_controller(dt)
        self.set_power(power)

    def get_slope(self):
        slope = self.interpolation.interpolate(
            self.get_speed(), self.get_power()
        )
        return slope

    def get_speed_error(self):
        speed_error = self.target_speed - self.motor.speed()
        return speed_error

    def run_slope_calibration(self):
        from pybricks.tools import StopWatch
        from utils.csv_file_handler import CSVFileHandler

        sw = StopWatch()

        res = []

        speeds = (CONSTANTS.DRIVE_MOTOR_TARGET_SPEED - 200, CONSTANTS.DRIVE_MOTOR_TARGET_SPEED, CONSTANTS.DRIVE_MOTOR_TARGET_SPEED + 200)
        slope_angles = range(-20, 25, 5) # -20 to 20 in 5er steps

        for deg in slope_angles:
            for target_speed in speeds:
                self.target_speed = target_speed
                RobotHub().await_user_confirmation(str(deg) + " deg")
                sw.reset()
                self.drive(target_speed)
                while not sw.time() > 500:
                     # wait 500ms so the drive motor can reach target speed
                    self.update(0.05)
                    continue
                values = []
                while not sw.time() > 2000:
                    values.append(self.get_dc())
                    self.update(0.05)
                res.append(
                    (target_speed, sum(values) / len(values), deg)
                )
                RobotHub().print(res)
                self.stop()

        # --- calibration done -> data storage
        with CSVFileHandler(CONSTANTS.DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH) as csv:
            csv.write_dict(res)

    def load_slope_calibration(self):
        from utils.csv_file_handler import CSVFileHandler

        with CSVFileHandler(CONSTANTS.DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH) as csv:
            self.interpolation = Interpolation2DFromArray(csv.read_dict())

@singleton
class DriveMotorAtConstantSpeed:
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port, gears=[CONSTANTS.GEAR_RATIO_DRIVE_MOTOR])
        self.motor.reset_angle(0)
        self.target_speed = CONSTANTS.DRIVE_MOTOR_TARGET_SPEED
        self.drive(self.target_speed)

    def drive(self, speed):
        if speed == 0:
            self.motor.hold()
        if speed > CONSTANTS.DRIVE_MOTOR_MAX_SPEED:
            raise MotorControlException("Drive Motor speed is set to a speed higher than DRIVE_MOTOR_MAX_SPEED")

        self.motor.run(speed)

    def update(self, dt):
        return
