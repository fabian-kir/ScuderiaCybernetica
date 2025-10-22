from Software.software_ev3.controllers.controller import Controller
from Software.software_ev3.core.utils import TimeFloorSchedule
from Software.software_ev3.hardware import slope_sensor
from Software.software_ev3.hardware.slope_sensor import SlopeSensor


class PlattformController:
    def __init__(self):
        main_controller = Controller()
        main_controller.register_update_handler(self.update)
        self.slope_sensor = SlopeSensor()

        self.total_angle = 0

        self.time_shedule = TimeFloorSchedule() # Mapped zurückgelegten Weg zu einzustellendem Winkel des kleinen Motors

    def update(self, dt):
        delta_angle = self.slope_sensor.get_slope_delta()
        self.total_angle += delta_angle * dt


