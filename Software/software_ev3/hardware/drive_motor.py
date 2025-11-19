from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from hardware.robot_hub import RobotHub

from utils.singleton import singleton
from utils.data_logger import log_data
from utils.interpolation_from_array import InterpolationFromArray


@singleton
class DriveMotor:
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port)
        self.motor.reset_angle(0)

        # Target speed (deg/s) - horizontal plane speed
        self.target_speed = 0

        # Current power output (-100 to 100)
        self._dc = 0

        # PID controller
        self.base_resistance = 0 # loaded during calibration

        self.kp = CONSTANTS.DRIVE_MOTOR_KP

        self.ki = CONSTANTS.DRIVE_MOTOR_KI
        self.max_integral = CONSTANTS.DRIVE_MOTOR_MAX_I

        self.kd = CONSTANTS.DRIVE_MOTOR_KD

        self.integral = 0.0
        self.previous_error = 0.0

        self.past_resistances = []

        self.interpolation = InterpolationFromArray(array=CONSTANTS.SLOPE_SPEED_ARRAY)

    def set_dc(self, power):
        if power == 0:
            self._dc = 0
            self.motor.hold()
            return
        
        elif 0 < abs(power) < CONSTANTS.DRIVE_MOTOR_MIN_POWER:
            self._dc = CONSTANTS.DRIVE_MOTOR_MIN_POWER
        
        elif 0 > abs(power) > CONSTANTS.DRIVE_MOTOR_MIN_POWER:
            self._dc = -CONSTANTS.DRIVE_MOTOR_MIN_POWER

        self._dc = power
        self.motor.dc(self._dc)

    def get_dc(self):
        return self._dc

    def drive(self, speed):
        if speed == 0:
            self.motor.hold()

        log_data("target_speed", speed)
        self.target_speed = speed

    def update(self, dt):
        log_data("drive_motor_speed", self.motor.speed())
        log_data("drive_motor_power", self.get_dc())
        log_data("target_speed", self.target_speed)

        RobotHub().print("Speed:", self.motor.speed())

        # self._pid_controller(dt) # currently not pid controlling speed

        self.drive_at_constant_power(dt)
        self._update_resistance()

    def drive_at_constant_power(self, dt):
        target_percent = CONSTANTS.DRIVE_MOTOR_CONSTANT_POWER / (RobotHub().get_battery_power())
        self.set_dc(target_percent * 100)

    def _pid_controller(self, dt):
        error = self.get_speed_error()

        # proportional
        p = self.kp * error
        log_data("p", p)

        # integral
        if abs(self.motor.speed()) < 5:
            # ensure motor doesn't overshoot so much when it was halted
            i = 0
            self.integral = 0
        else:
            self.integral += error * dt
            i = self.ki * self.integral
            i = min(max(i, -self.max_integral), self.max_integral)
        log_data("i", i)


        # derivative
        derivative = (error - self.previous_error) / dt
        d = self.kd * derivative
        log_data("d", d)

        self.set_dc(p + i + d)
        self.previous_error = error

    def get_slope_angle(self):
        return self.interpolation.interpolate(self.motor.speed())

    def run_calibration(self):
        from pybricks.tools import wait

        RobotHub().await_user_confirmation("0 deg")
        RobotHub().print("0 deg")
        self.drive_at_constant_power(1)
        
        wait(1000)
        
        values = []
        for i in range(50):
            speed = self.motor.speed()
            values.append(self.motor.speed())
            wait(50)

        self.motor.stop()
        RobotHub().print("AVG:", sum(values) / len(values))
        RobotHub().print("\n\n\n")

        # ---
        RobotHub().await_user_confirmation("5 deg")
        RobotHub().print("5 deg")
        self.drive_at_constant_power(1)
        
        wait(1000)
        
        values = []
        for i in range(50):
            speed = self.motor.speed()
            values.append(self.motor.speed())
            wait(50)

        self.motor.stop()
        RobotHub().print("AVG:", sum(values) / len(values))
        RobotHub().print("\n\n\n")

        # ---
        RobotHub().await_user_confirmation("10 deg")
        RobotHub().print("10 deg")
        self.drive_at_constant_power(1)
        
        wait(1000)
        
        values = []
        for i in range(50):
            speed = self.motor.speed()
            values.append(self.motor.speed())
            wait(50)

        self.motor.stop()
        RobotHub().print("AVG:", sum(values) / len(values))
        RobotHub().print("\n\n\n")

        # ---
        RobotHub().await_user_confirmation("-5 deg")
        RobotHub().print("-5 deg")
        self.drive_at_constant_power(1)
        
        wait(1000)
        
        values = []
        for i in range(50):
            speed = self.motor.speed()
            values.append(self.motor.speed())
            wait(50)

        self.motor.stop()
        RobotHub().print("AVG:", sum(values) / len(values))
        RobotHub().print("\n\n\n")

        # ---
        RobotHub().await_user_confirmation("-10 deg")
        RobotHub().print("-10 deg")
        self.drive_at_constant_power(1)
        
        wait(1000)
        
        values = []
        for i in range(50):
            speed = self.motor.speed()
            values.append(self.motor.speed())
            wait(50)

        self.motor.stop()
        RobotHub().print("AVG:", sum(values) / len(values))
        RobotHub().print("\n\n\n")

        # ---



    def get_speed_error(self):
        speed_error = self.target_speed - self.motor.speed()
        return speed_error