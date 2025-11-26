from software_ev3.config.ports import PORTS
from software_ev3.config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from software_ev3.hardware.robot_hub import RobotHub

from software_ev3.exceptions import MotorControlException

from software_ev3.utils.controllers import PIDController
from software_ev3.utils.singleton import singleton
from software_ev3.utils.data_logger import log_data
from math import copysign

from software_ev3.utils.csv_file_handler import CSVFileHandler


@singleton
class DriveMotor:
    def __init__(self, run_slope_calibration=False):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port, gears=CONSTANTS.GEARS_DRIVE_MOTOR)
        self.motor.reset_angle(0)

        self._calibration_lookup = {}
        self._calibration_speeds = []

        self._power = 0

        self.pid_controller = PIDController(
            kp=CONSTANTS.DRIVE_MOTOR_KP,
            ki=CONSTANTS.DRIVE_MOTOR_KI,
            kd=CONSTANTS.DRIVE_MOTOR_KD,
            get_state=self.get_speed,
            max_i=CONSTANTS.DRIVE_MOTOR_MAX_I
        )

        # Target speed (deg/s)
        self.target_speed = CONSTANTS.DRIVE_MOTOR_TARGET_SPEED
        self.drive(self.target_speed)

        if run_slope_calibration:
            self.run_slope_calibration()
        self.load_slope_calibration()  # loads the calibration data from last calibration and creates interpolation

    def stop(self):
        self.set_power(0)
        self.motor.stop()
        self.target_speed = 0
        self.pid_controller.reset()

    def get_speed(self):
        return self.motor.speed()

    def set_power(self, power):
        if power == 0:
            self._power = 0
            self.motor.hold()
            return

        if abs(power) < CONSTANTS.DRIVE_MOTOR_MIN_POWER:
            power = copysign(CONSTANTS.DRIVE_MOTOR_MIN_POWER, power)

        battery_voltage = RobotHub().get_battery_voltage()
        if battery_voltage <= 0:
            raise MotorControlException("Battery voltage reading must be positive.")

        # Clamp requested power so we never exceed available voltage
        bounded_power = max(min(power, battery_voltage), -battery_voltage)
        duty_cycle = (bounded_power / battery_voltage) * 100
        duty_cycle = max(min(duty_cycle, 100), -100)

        self._power = bounded_power
        self.motor.dc(duty_cycle)

    def get_power(self):
        return self._power

    def drive(self, speed):
        if speed == 0:
            self.motor.hold()

        if abs(speed) > CONSTANTS.DRIVE_MOTOR_MAX_SPEED:
            raise MotorControlException("Drive Motor speed is set to a speed higher than DRIVE_MOTOR_MAX_SPEED")

        log_data("target_speed", speed)
        self.target_speed = speed
        # Synchronize PID controller with the latest target so it ramps power accordingly.
        self.pid_controller.set_target(speed)

    def update(self, dt):
        log_data("drive_motor_speed", self.motor.speed())
        log_data("drive_motor_power", self.get_power())
        log_data("target_speed", self.target_speed)

        # PID Control Speed:
        power = self.pid_controller(dt)
        self.set_power(power)

    def get_slope(self):
        if not self._calibration_lookup:
            return 0
        return self._interpolate_slope(self.get_speed(), self.get_power())

    def get_speed_error(self):
        speed_error = self.target_speed - self.motor.speed()
        return speed_error

    def run_slope_calibration(self):
        from pybricks.tools import StopWatch, wait

        sw = StopWatch()

        res = []

        speeds = (CONSTANTS.DRIVE_MOTOR_TARGET_SPEED - 200, CONSTANTS.DRIVE_MOTOR_TARGET_SPEED, CONSTANTS.DRIVE_MOTOR_TARGET_SPEED + 200)
        slope_angles = range(-20, 25, 5) # -20 to 20 in 5er steps

        for deg in slope_angles:
            for target_speed in speeds:
                self.target_speed = target_speed
                RobotHub().await_user_confirmation(str(deg) + " deg")
                sw.reset()
                self.pid_controller.reset()
                self.drive(target_speed)
                while not sw.time() > 500:
                    # Warm up for 500 ms so the drive motor can reach target speed
                    self.update(0.05)
                    wait(50)
                values = []
                while not sw.time() > 2000:
                    values.append(self.get_power())
                    self.update(0.05)
                    wait(50)
                average_power = sum(values) / len(values) if values else 0
                res.append(
                    {
                        "speed": target_speed,
                        "power": average_power,
                        "slope": deg
                    }
                )
                RobotHub().print("Calibration point:", res[-1])
                self.stop()
                self.pid_controller.reset()

        # --- calibration done -> data storage
        with CSVFileHandler(CONSTANTS.DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH, mode='w') as csv:
            csv.write_dict(res)
        self.load_slope_calibration()

    def load_slope_calibration(self):
        with CSVFileHandler(CONSTANTS.DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH, mode='r') as csv:
            calibration_rows = csv.read_dict()

        if not calibration_rows:
            RobotHub().print("Drive motor slope calibration file is empty.")
            self._calibration_lookup = {}
            self._calibration_speeds = []
            return

        self._build_calibration_lookup(calibration_rows)

    def _build_calibration_lookup(self, rows):
        lookup = {}

        for row in rows:
            try:
                if isinstance(row, dict):
                    speed = float(row["speed"])
                    power = float(row["power"])
                    slope = float(row["slope"])
                else:
                    speed, power, slope = row
                    speed = float(speed)
                    power = float(power)
                    slope = float(slope)
            except (KeyError, TypeError, ValueError):
                continue

            lookup.setdefault(speed, []).append((power, slope))

        for speed in lookup:
            lookup[speed].sort(key=lambda pair: pair[0])

        self._calibration_lookup = lookup
        self._calibration_speeds = sorted(lookup.keys())

    def _slope_for_speed(self, speed_key, power):
        points = self._calibration_lookup.get(speed_key)
        if not points:
            return 0

        if len(points) == 1:
            return points[0][1]

        if power <= points[0][0]:
            return points[0][1]

        if power >= points[-1][0]:
            return points[-1][1]

        for idx in range(len(points) - 1):
            p1, s1 = points[idx]
            p2, s2 = points[idx + 1]
            if p1 <= power <= p2:
                if p2 == p1:
                    return s2
                ratio = (power - p1) / (p2 - p1)
                return s1 + ratio * (s2 - s1)

        return points[-1][1]

    def _interpolate_slope(self, speed, power):
        if not self._calibration_speeds:
            return 0

        speeds = self._calibration_speeds

        if speed <= speeds[0]:
            return self._slope_for_speed(speeds[0], power)

        if speed >= speeds[-1]:
            return self._slope_for_speed(speeds[-1], power)

        for idx in range(len(speeds) - 1):
            low = speeds[idx]
            high = speeds[idx + 1]
            if low <= speed <= high:
                slope_low = self._slope_for_speed(low, power)
                slope_high = self._slope_for_speed(high, power)
                if high == low:
                    return slope_low
                ratio = (speed - low) / (high - low)
                return slope_low + ratio * (slope_high - slope_low)

        return self._slope_for_speed(speeds[-1], power)

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
