from pybricks.robotics import DriveBase

from Software.software_ev3.config.constants import CONSTANTS
from Software.software_ev3.controllers.controller import Controller
from Software.software_ev3.core.utils import TimeFloorSchedule
from Software.software_ev3.hardware import slope_sensor
from Software.software_ev3.hardware.balance_motor import BalanceMotor
from Software.software_ev3.hardware.power_train import PowerTrain
from Software.software_ev3.hardware.slope_sensor import SlopeSensor


class PlattformController:
    def __init__(self):
        self.slope_sensor = SlopeSensor()
        self.power_train = PowerTrain()
        self.balance_motor = BalanceMotor()

        self.total_angle = 0

        self.time_shedule = TimeFloorSchedule() # Mapped zurückgelegten Weg zu einzustellendem Winkel des kleinen Motors
        self.drive_axle_sleds_distance = CONSTANTS["DRIVE_AXLE_SLED_DISTANCE"]

    def update(self, dt):
        raise Exception("PlattformController is not supposed to be updated directly. Only Hardware Components should be updated. Controller ticks happen due to .control()")

    def _adjust_small_motor(self):
        angle = self.time_shedule.consume(self.power_train.get_absolute_distance())
        self.balance_motor.move_to(angle)

    def control(self, dt):
        total_distance = self.power_train.get_absolute_distance()
        ds = self.power_train.travelled_since_last_update()
        d_angle = self.slope_sensor.get_slope_delta()

        self.total_angle += d_angle * ds
        self.time_shedule.put(total_distance + self.drive_axle_sleds_distance, -self.total_angle)




