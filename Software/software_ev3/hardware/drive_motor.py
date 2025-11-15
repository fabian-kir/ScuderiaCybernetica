from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from hardware.robot_hub import RobotHub

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
        self.base_resistance = CONSTANTS["DRIVE_MOTOR_BASE_RESISTANCE"]

        self.kp = CONSTANTS["DRIVE_MOTOR_KP"]

        self.ki = CONSTANTS["DRIVE_MOTOR_KI"]
        self.max_integral = CONSTANTS["DRIVE_MOTOR_MAX_I"]

        self.kd = CONSTANTS["DRIVE_MOTOR_KD"]
        self.kslope = CONSTANTS["SPEED_COMPENSATION_PER_RESISTANCE"]

        self.integral = 0.0
        self.previous_error = 0.0

        self.past_resistances = []

    def set_power(self, power):
        self._power = power
        self.motor.dc(self._power)

    def get_power(self):
        return self._power

    def drive(self, speed):
        log_data("target_speed", speed)
        self.target_speed = speed

    def update(self, dt):
        log_data("drive_motor_speed", self.motor.speed())
        log_data("drive_motor_power", self.get_power())
        log_data("target_speed", self.target_speed)

        self._pid_controller(dt)
        self._update_resistance()
        self._slope_correction(dt)

    def _pid_controller(self, dt):
        error = self.get_speed_error()

        # proportional
        p = self.kp * error
        log_data("p", p)

        # integral
        if abs(self.motor.speed() < 5):
            # ensure motor doesn't overshoot so much when it was halted
            i = 0
            self.integral = 0
        else:
            self.integral += error * dt
            i = self.ki * self.integral
            i = min(max(i, -self.max_integral), self.max_integral)
        log_data("i", i)


        # derivative
        derivative = (error * dt) / dt
        d = self.kd * derivative
        log_data("d", d)

        self.set_power(p + i + d)
        self.previous_error = error

    def get_resistance(self, n=5):
        '''Returns the resistance averaged accross last n updates.
            Resistance means how much more power output realtes to how much speed gain
        '''
        return sum(self.past_resistances[-n:]) / n if len(self.past_resistances) >= n else 0.0

    def _update_resistance(self):
        if self.get_power() == 0:
            self.past_resistances = [self.base_resistance] * 10
            return

        '''Adds a new resistance measurement to the past measurements.'''
        resistance = self.motor.speed() / self.get_power() # in (rad / s) / V
        self.past_resistances.append(resistance)

    def get_speed_error(self):
        speed_error = self.target_speed - self.motor.speed()
        return speed_error

    def _slope_correction(self, dt):
        return
        resistance = self.get_resistance()
        slope_correction = self.kslope * (resistance) + self.base_resistance
        self.drive(self._power + slope_correction) # using "drive" methode is wrong