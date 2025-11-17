from config.constants import CONSTANTS
from utils.singleton import singleton


@singleton
class CalibrationData:
    def __init__(self):
        self.path_to_file = CONSTANTS.PATH_TO_CALIBRATION_DATA

        self.ultrasound_sensor_target_distance = None
        self.color_sensor_target_reflection = None
        self.drive_motor_base_resistance = None

    def load_from_file(self):
        with open(self.path_to_file, "r") as file:
            for line in file.readlines():
                line = line.strip("")
                if line.startswith("ultrasound_sensor_target_distance"):
                    self.ultrasound_sensor_target_distance = float(line.split("=")[1])
                elif line.startswith("color_sensor_target_reflection"):
                    self.color_sensor_target_reflection = float(line.split("=")[1])
                elif line.startswith("drive_motor_base_resistance"):
                    self.drive_motor_base_resistance = float(line.split("=")[1])

    def save_to_file(self):
        lines = [
            "ultrasound_sensor_target_distance=" + str(self.ultrasound_sensor_target_distance)+ "\n"
            "color_sensor_target_reflection=" + str(self.ultrasound_sensor_target_distance)+ "\n"
            "drive_motor_base_resistance=" + str(self.ultrasound_sensor_target_distance) + "\n"
        ]

        with open(self.path_to_file, "w") as file:
            file.writelines(lines)

calibration_data = CalibrationData()