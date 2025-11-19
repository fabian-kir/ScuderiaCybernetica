from config.constants import CONSTANTS
from utils.singleton import singleton


@singleton
class CalibrationData:
    def __init__(self):
        self.path_to_file = CONSTANTS.PATH_TO_CALIBRATION_DATA

        self.color_sensor_target_reflection = None
        self.drive_motor_base_resistance = None

    def load_from_file(self):
        with open(self.path_to_file, "r") as file:
            for line in file.readlines():
                line = line.strip("")
                #if line.startswith("ultrasound_sensor_target_distance"):
                    #self.ultrasound_sensor_target_distance = float(line.split("=")[1])
                if line.startswith("color_sensor_target_reflection"):
                    self.color_sensor_target_reflection = float(line.split("=")[1])

    def safe_to_file(self):
        if self.drive_motor_base_resistance is None:
            self.drive_motor_base_resistance = 0
        if self.color_sensor_target_reflection is None:
            self.color_sensor_target_reflection = 0

        lines = [
            "color_sensor_target_reflection=" + str(self.color_sensor_target_reflection)+ "\n"
        ]

        text = ""
        for linetext in lines:
            text += linetext
        print(text)

        with open(self.path_to_file, "w") as file:
            file.write(text)

calibration_data = CalibrationData()