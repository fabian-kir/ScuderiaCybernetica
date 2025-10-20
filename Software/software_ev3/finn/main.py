#!/usr/bin/env pybricks-micropython
# main.py
from pybricks.tools import StopWatch, wait
from robot import Robot

# Testfahrt
bot = Robot()
i = 0 
while i < 10000 : 
    bot.robot.drive(100, 0)
    bot.balance(0.024)
    i += 1

#bot.wallFollower(100, 100, 0.4)

#bot.wallFollower(100, 100, 0.4)