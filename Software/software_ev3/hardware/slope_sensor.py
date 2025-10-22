from .hardware_wrapper import HardwareWrapper
from ..config.ports import PORTS
from ..exceptions import CalibrationDataDoesntExistsException

from pybricks.ev3devices import ColorSensor
from pybricks.tools import wait

from sklearn.linear_model import LinearRegression
import json

class SlopeSensor(HardwareWrapper):
    def __init__(self):
        self.port = PORTS["COLOR_SENSOR"]
        self.sensor = ColorSensor(self.port)

        self.calibration_model_slope = None
        self.calibration_model_intercept = None

        try:
            self.load_calibration_data()
        except CalibrationDataDoesntExistsException:
            self.calibrate()

    def load_calibration_data(self):
        with open("calibration_data.json", "r") as json_file:
            calibration_data = json.load(json_file)

            try:
                self.calibration_model_slope = calibration_data["COLOR_SENSOR_CALIBRATION_SLOPE"]
                self.calibration_model_intercept = calibration_data["COLOR_SENSOR_CALIBRATION_INTERCEPT"]

                assert self.calibration_model_slope is not None and type(self.calibration_model_slope) == float
                assert self.calibration_model_intercept is not None and type(self.calibration_model_intercept) == float
            except (KeyError, AssertionError) as exception:
                raise CalibrationDataDoesntExistsException("Calibration data does not exist or is corrupted.")

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

        # safe calibration data to calibrations.json
        with open("calibration_data.json", "w") as json_file:
            json.dump({
                "COLOR_SENSOR_CALIBRATION_SLOPE": model.coef_[0],
                "COLOR_SENSOR_CALIBRATION_INTERCEPT": model.intercept_
            }, json_file)

        # happens through an extra load - not really necessary, but good to ensure no hidden bugs are missed in the loading process!
        self.load_calibration_data()

    def get_slope_delta(self):
        """
        Returns the current angle between wheels and slope detection sleds.
        WARNINING: this is only the change in the slope, not slop itself
        """