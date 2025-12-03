from software_ev3.hardware.robot_hub import RobotHub
from software_ev3.hardware.color_sensor import ColorSensor
from software_ev3.hardware.platform_motors import PlatformMotors
from software_ev3.hardware.ultrasonic_sensor import UltrasonicSensor
from software_ev3.config.constants import CONSTANTS
from pybricks.tools import StopWatch, wait
import math

from software_ev3.utils.data_logger import log_data

from software_ev3.hardware.drive_motor import DriveMotor


class PlatformController:
    def __init__(self):
        self.hub = RobotHub()
        self.color_sensor = ColorSensor()
        self.drive_motor = DriveMotor()
        self.platform_motors = PlatformMotors()
        self.ultrasonic_sensor = UltrasonicSensor()

        self.time_since_startup = 0

        self.sideways_last_error = 0
        self.sideways_integral = 0

        self.angle_smooth = self.platform_motors.forward_get_angle()
        self.alpha = 0.2

    def update(self, dt):
        if not self.controller_ready(dt):
            return

        self.sideways_proportional_speed_control(dt , 0.7, 0.002, 10)
        self.forward_mathematical_speed_control(dt)

    def sideways_proportional_speed_control(self, dt, kp, ki, kd):
 
        y_error = 63 - self.color_sensor.get_reflection()
        dt = dt * 1000
        if dt != 0:
            derivative = (y_error - self.sideways_last_error) / dt 
        else : 
            derivative = 0   
        
        self.sideways_last_error = y_error

        self.sideways_integral = self.sideways_integral * 0.95 + y_error * dt

        power = (-1) * (y_error * (kp) + derivative * kd + self.sideways_integral * ki)
        if self.platform_motors.sideways_get_angle() > 10 and y_error < 0:
            power = 0
        if self.platform_motors.sideways_get_angle() < -10 and y_error > 0:
            power = 0
        print(dt ,y_error, self.sideways_integral, derivative )

    
        self.platform_motors.run_sideways(power)

    def forward_proportional_speed_control(self, dt):
        slope_soll = self.ultrasonic_sensor.get_distance_error()        
        slope_ist = self.platform_motors.forward_get_angle()
        error = slope_soll - slope_ist
        self.platform_motors.forward_set_speed(error * CONSTANTS.PLATFORM_FORWARD_SPEED_KP,
                                               ramp_up_speed_to_min=True)
        
    def forward_mathematical_speed_control(self, dt):
        #calculatiung the angle 
        x = self.ultrasonic_sensor.get_distance()
        angle_desired = 0.0009 * x**2 - 0.5774 *x + 52.877

        
        self.angle_smooth = self.angle_smooth + self.alpha * (angle_desired - self.angle_smooth)

        if self.angle_smooth < -20 * 8.35:
            target = -20
        elif self.angle_smooth > 20 * 8.35:
            target = 20
        else :
            target = self.angle_smooth
    
        self.platform_motors.forward_track_target( target *8.35)

    def controller_ready(self, dt):
        self.time_since_startup += dt
        if self.time_since_startup >= CONSTANTS.TIME_UNTIL_PLATFORM_CONTROLLER_STARTS:
            return True
        return False