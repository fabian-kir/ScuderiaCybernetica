"""
Data logger for robot data collection.

Uses only standard library to ensure compatibility with EV3 robot.
Data is saved in CSV format for easy parsing and plotting later.
"""
import csv
import os
from time import time
from utils.singleton import singleton


@singleton
class DataLogger:
    """
    Singleton data logger that saves robot data to CSV files.

    Usage:
        logger = DataLogger()
        logger.log_data(stream_name="motor_speed", dt=0.01, value=45.5)
    """

    def __init__(self, log_file="robot_data.csv", enabled=True):
        """
        Initialize the data logger.

        Args:
            log_file: Path to the log file (default: "robot_data.csv")
            enabled: Whether logging is enabled (default: True)
        """
        self.log_file = log_file
        self.enabled = enabled
        self.start_time = time()
        self._file_handle = None
        self._writer = None
        self._ensure_file_initialized()

    def _ensure_file_initialized(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not self.enabled:
            return

        file_exists = os.path.exists(self.log_file)

        # Open file in append mode
        self._file_handle = open(self.log_file, 'a', newline='')
        self._writer = csv.writer(self._file_handle)

        # Write header if file is new
        if not file_exists:
            self._writer.writerow(['timestamp', 'elapsed_time', 'stream_name', 'dt', 'value'])
            self._file_handle.flush()

    def log_data(self, stream_name, dt, value):
        """
        Log a data point.

        Args:
            stream_name: Name of the data stream (e.g., "motor_speed", "angle")
            dt: Time delta in seconds since last update
            value: The value to log (can be int or float)
        """
        if not self.enabled:
            return

        try:
            current_time = time()
            elapsed_time = current_time - self.start_time

            # Write data row: timestamp, elapsed_time, stream_name, dt, value
            self._writer.writerow([
                current_time,
                elapsed_time,
                stream_name,
                dt,
                value
            ])
            self._file_handle.flush()  # Ensure data is written immediately

        except Exception as e:
            # Silently fail to avoid disrupting robot operation
            # In production, you might want to log this somehow
            pass

    def close(self):
        """Close the log file. Call this when done logging."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
            self._writer = None

    def set_enabled(self, enabled):
        """Enable or disable logging."""
        if self.enabled == enabled:
            return

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


def log_data(stream_name, dt, value):
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
    _logger_instance.log_data(stream_name, dt, value)

