"""
Data logger for robot data collection.

Uses only MicroPython-compatible modules to ensure compatibility with EV3 robot.
Data is saved in CSV format for easy parsing and plotting later.
"""

from time import time

from pybricks.tools import StopWatch
from software_ev3.utils.singleton import singleton

from software_ev3.hardware.robot_hub import RobotHub
from software_ev3.utils.csv_file_handler import CSVFileHandler


@singleton
class DataLogger:
    """
    Singleton data logger that saves robot data to CSV files.

    Usage:
        logger = DataLogger()
        logger.log_data(stream_name="motor_speed", value=45.5)
    """

    def __init__(self, log_file="robot_data.csv", enabled=True):
        """
        Initialize the data logger.

        Args:
            log_file: Path to the log file (default: "robot_data.csv")
            enabled: Whether logging is enabled (default: True)
        """
        self.stop_watch = StopWatch()

        self.log_file = log_file
        self.enabled = enabled
        self.start_time = self.stop_watch.time()
        self._file_handle = None
        self._file_initialized = False
        self._ensure_file_initialized()

    def _file_exists(self):
        """Check if the log file exists (MicroPython compatible)."""
        try:
            f = open(self.log_file, 'r')
            f.close()
            return True
        except OSError:
            return False

    def _format_csv_row(self, values):
        """
        Format a list of values as a CSV row.

        Args:
            values: List of values to format

        Returns:
            str: CSV-formatted row string
        """
        # Convert all values to strings and escape if needed
        formatted = []
        for value in values:
            str_value = str(value)
            # If value contains comma, quote, or newline, wrap in quotes and escape quotes
            if ',' in str_value or '"' in str_value or '\n' in str_value:
                str_value = '"' + str_value.replace('"', '""') + '"'
            formatted.append(str_value)
        return ','.join(formatted)

    def _ensure_file_initialized(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not self.enabled:
            return

        # Check if file exists and needs header
        file_needs_header = not self._file_exists()

        # Open file in append mode (MicroPython compatible)
        try:
            self._file_handle = CSVFileHandler(self.log_file, mode='a').__enter__()

            # Write header if file is new
            if file_needs_header:
                self._file_handle.write_row(['stream_name', 'time', 'value'])

            self._file_initialized = True
        except Exception:
            RobotHub().print("Error opening log file:", self.log_file)
            # Silently fail to avoid disrupting robot operation
            self._file_handle = None
            self._file_initialized = False

    def log_data(self, stream_name, value):
        """
        Log a data point.

        Args:
            stream_name: Name of the data stream (e.g., "motor_speed", "angle")
            value: The value to log (can be int or float)
        """
        time = self.stop_watch.time()

        if not self.enabled:
            return

        # Re-initialize file if needed
        if not self._file_initialized or self._file_handle is None:
            self._ensure_file_initialized()
            if not self._file_initialized:
                RobotHub().print("Error re-initializing log file")
                return

        try:

            # Format and write data row: stream_name, time, value
            self._file_handle.write_row([stream_name, time, value])

        except Exception:
            # Silently fail to avoid disrupting robot operation
            # Close file handle so it can be re-opened next time
            RobotHub().print("Error logging data to file")
            if self._file_handle:
                try:
                    self._file_handle.__exit__(None, None, None)
                except Exception:
                    pass
                self._file_handle = None
                self._file_initialized = False

    def close(self):
        """Close the log file. Call this when done logging."""
        if self._file_handle:
            try:
                self._file_handle.__exit__(None, None, None)
            except Exception:
                pass
            self._file_handle = None
            self._file_initialized = False

    def set_enabled(self, enabled):
        self.enabled = enabled
        if enabled:
            self._ensure_file_initialized()
        else:
            self.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Convenience function for easy access
# Usage: from utils.data_logger import log_data; log_data("stream_name", dt=0.01, value=42)
_logger_instance = None


def log_data(stream_name, value):
    """
    Convenience function to log data without needing to get the logger instance.

    Usage:
        from utils.data_logger import log_data
        log_data(stream_name="motor_speed", dt=0.01, value=45.5)

    Args:
        stream_name: Name of the data stream
        dt: Time delta in seconds since last update
        value: The value to log
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = DataLogger()
    _logger_instance.log_data(stream_name, value)
