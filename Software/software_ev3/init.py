from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, Image

left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
balance_motor = Motor(Port.C)

color_sensor = ColorSensor(Port.S1)
distance_sensor = UltrasonicSensor(Port.S2)