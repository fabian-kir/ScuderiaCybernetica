#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from time import sleep

motor = Motor(Port.C)

motor.run(1000)
sleep(1)

