from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from utils.singleton import singleton
from utils.data_logger import log_data


@singleton
class DriveMotor:
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port)
        self.motor.reset_angle(0)

        # Target speed (deg/s) - horizontal plane speed
        self.target_speed = 0

        # Current power output (-100 to 100)
        self._power = 0

        # PID controller
        self.base_resistance = CONSTANTS.get("DRIVE_MOTOR_BASE_RESISTANCE", 0.0001)

        self.kp = CONSTANTS.get("DRIVE_MOTOR_KP", 1)
        self.ki = CONSTANTS.get("DRIVE_MOTOR_KI", 1)
        self.kd = CONSTANTS.get("DRIVE_MOTOR_KD", 0)
        self.kslope = CONSTANTS.get("SPEED_COMPENSATION_PER_RESISTANCE", 0.0001)

        self.integral = 0.0
        self.previous_error = 0.0

        self.past_resistances = []

    def set_power(self, power):
        self._power = power
        self.motor.dc(self._power)

    def get_power(self):
        return self._power

    def drive(self, speed):
        self.target_speed = speed

    def update(self, dt):
        log_data("drive_motor_speed", dt, self.motor.speed())
        log_data("drive_motor_power", dt, self.get_power())

        self._pid_controller(dt)
        self._update_resistance()
        self._slope_correction(dt)

    def _pid_controller(self, dt):
        error = self.get_speed_error()

        # proportional
        p = self.kp * error

        # integral
        self.integral += error * dt
        i = self.ki * self.integral

        # derivative
        derivative = (error * dt) / dt
        d = self.kd * derivative

        self.set_power(p + i + d)
        self.previous_error = error

    def get_resistance(self, n=5):
        '''Returns the resistance averaged accross last n updates.
            Resistance means how much more power output realtes to how much speed gain
        '''
        return sum(self.past_resistances[-n:]) / n if len(self.past_resistances) >= n else 0.0

    def _update_resistance(self):
        '''Adds a new resistance measurement to the past measurements.'''
        resistance = self.motor.speed() / self.get_power() # in (rad / s) / V
        self.past_resistances.append(resistance)

    def get_speed_error(self):
        return self.target_speed - self.motor.speed()

    def _slope_correction(self, dt):
        resistance = self.get_resistance()
        slope_correction = self.kslope * (resistance) + self.base_resistance
        self.drive(self._power + slope_correction)