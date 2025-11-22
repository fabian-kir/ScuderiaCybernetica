
from pybricks.ev3devices import Motor
from pybricks.tools import wait
from pybri

motor = Motor(Port.A)

for i in range(120):
    motor.track_target(i)
    wait (int(i/2) * 10)
    motor.track_target(-i)
    wait (int(i/2) * 10)
