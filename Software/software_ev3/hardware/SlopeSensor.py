from pybricks.ev3devices import ColorSensor
from pybricks.tools import wait


class SlopeSensor:
    def __init__(self, sensor):
        self.sensor = sensor
        self.baseline = None
        self.calibrated = False

    @classmethod
    def init(cls, port):
        sensor = ColorSensor(port)
        return cls(sensor)

    def calibrate(self):
        #TODO:calibration logic
        self.calibrated = True

    def get_slope(self):
        if not self.calibrated:
            raise RuntimeError("SlopeSensor not calibrated yet.")
        return None
