from config.ports import PORTS
from pybricks.ev3devices import TouchSensor
from pybricks.parameters import Stop

from utils.singleton import singleton
from config.constants import CONSTANTS

from hardware.robot_hub import RobotHub

@singleton
class TouchSensors:
    def __init__(self):
        self.port_left = PORTS["LEFT_TOUCH_SENSOR"] 
        self.port_right = PORTS["RIGHT_TOUCH_SENSOR"] 

        self.touch_sensor_left = TouchSensor(self.port_left)
        self.touch_sensor_right = TouchSensor(self.port_right)

    def update(self, dt):
        return

    def is_left_pressed(self):
        return self.touch_sensor_left.pressed()
        
    def is_right_pressed(self):
        return self.touch_sensor_right.pressed()
    
    def is_any_pressed(self):
        return self.touch_sensor_left.pressed() or self.touch_sensor_right.pressed()
