from ..config.ports import PORTS
from pybricks.ev3devices import ColorSensor
from pybricks.tools import wait

from sklearn.linear_model import LinearRegression

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
        from robot_hub import RobotHub
        hub = RobotHub()

        self.calibration_data = {} # dict: keys <=> angle, values <=> reflection strength

        # TODO kalibriert derzeit nur Lichtreflexion <=> Steigungsgrad. Eventuell noch manuelle kalibrierung der Transportplatte hinzufügen

        # Slope 0°
        hub.display("Place on 0° slope, then press middle button")
        hub.await_user_confirmation()
        wait(100)
        self.calibration_data[0] = self.sensor.reflection()
        hub.beep()

        # Slope 5°
        hub.display("Place on 5° slope, then press middle button")
        hub.await_user_confirmation()
        wait(100)
        self.calibration_data[5] = self.sensor.reflection()
        hub.beep()

        # Slope 15°
        hub.display("Place on 15° slope, then press middle button")
        hub.await_user_confirmation()
        wait(100)
        self.calibration_data[15] = self.sensor.reflection()
        hub.beep()

        # Slope -5°
        hub.display("Place on -5° slope, then press middle button")
        hub.await_user_confirmation()
        wait(100)
        self.calibration_data[-5] = self.sensor.reflection()
        hub.beep()

        # Slope -15°
        hub.display("Place on -15° slope, then press middle button")
        hub.await_user_confirmation()
        wait(100)
        self.calibration_data[-15] = self.sensor.reflection()
        hub.beep()

        print("Calibration data created:", self.calibration_data)

        # Lineare Regression über die Datenpunkte um Funktion zu erhalten
        # Reflexiongrad -> Winkeländerung

        model = LinearRegression()
        x = list(self.calibration_data.keys())
        y = list(self.calibration_data.values())
        model.fit(x, y)
        print("Calculated a linear regression model to fit reflection strength to slope angle, \nwith a score of:", model.score(x, y))
        print("slope:", model.coef_)
        print("intercept:", model.intercept_)

        self.get_angle = lambda self: model.predict([self.sensor.reflection()])[0] # This is not how to add methods: TODO clean this mess up!

        # TODO safe calibration data so it doesn't need to be repeated again and again!

        self.calibrated = True

    def get_slope(self) -> int:
        if not self.calibrated:
            raise RuntimeError("SlopeSensor not calibrated yet.")