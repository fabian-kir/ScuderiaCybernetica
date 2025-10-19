from config.ports import PORTS
from pybricks.ev3devices import ColorSensor
from pybricks.tools import wait


class SlopeSensor:
    _instance = None
    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self):
        self.port = PORTS["COLOR_SENSOR"]
        self.sensor = ColorSensor(self.port)

        self.baseline = None
        self.calibrated = False

        self.create_baseline() # TODO maybe this needs to be made more complicated because it might require user intervention like
                                   # positioning the robot correctly, etc...
        self.calibrate() # TODO this could be the same as creating the baseline

    def calibrate(self):
        #TODO:calibration logic
        self.calibrated = True

    def get_slope(self) -> int:
        if not self.calibrated:
            raise RuntimeError("SlopeSensor not calibrated yet.")