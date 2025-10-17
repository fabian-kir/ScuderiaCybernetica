#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import ColorSensor
from pybricks.parameters import Port

# Create your objects here.
ev3 = EV3Brick()

color_sensor = ColorSensor(Port.S1)

for i in range (1_000_000):
    print(color_sensor.reflection())