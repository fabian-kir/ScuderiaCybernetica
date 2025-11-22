from config.constants import CONSTANTS
from utils.singleton import singleton
from csv_file_handler import CSVFileHandler


@singleton
class CalibrationData:
    def __init__(self):
        self.path_to_file = CONSTANTS.PATH_TO_CALIBRATION_DATA
        self.values = {}

    def load_from_file(self):
        with CSVFileHandler(self.path_to_file, mode='r') as csv:
            for row in csv.read_all():
                if len(row) == 2:
                    key, val = row
                    try:
                        self.values[key] = eval(val)
                    except Exception:
                        print(f"Warning: Failed to parse value for {key}: {val}")

    def safe_to_file(self):
        with CSVFileHandler(self.path_to_file, mode='w') as csv:
            for key, val in self.values.items():
                csv.write_row([key, repr(val)])

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value


calibration_data = CalibrationData()