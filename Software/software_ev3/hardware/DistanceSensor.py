from pybricks.ev3devices import UltrasonicSensor

class DistanceSensor:
    def __init__(self, sensor):
        self.sensor = sensor

    @classmethod
    def init(cls, port):
        print("Setting up sensor on port:", port)
        sensor = UltrasonicSensor(port)
        return cls(sensor)