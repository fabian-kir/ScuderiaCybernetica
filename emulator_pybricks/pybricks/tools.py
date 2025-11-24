"""
Pybricks tools module emulation

Provides timing and utility functions.
"""

import time


class StopWatch:
    """
    A stopwatch to measure time intervals.
    
    Similar to the pybricks StopWatch, measures time in milliseconds.
    """
    
    def __init__(self):
        """Initialize the stopwatch and start counting"""
        self._start_time = time.time()
        self._pause_time = None
        self._paused_duration = 0
    
    def time(self) -> int:
        """
        Get the current time of the stopwatch.
        
        Returns:
            Time in milliseconds since the stopwatch was started or reset
        """
        if self._pause_time is not None:
            # Currently paused
            elapsed = (self._pause_time - self._start_time - self._paused_duration) * 1000
        else:
            elapsed = (time.time() - self._start_time - self._paused_duration) * 1000
        return int(elapsed)
    
    def pause(self):
        """Pause the stopwatch"""
        if self._pause_time is None:
            self._pause_time = time.time()
    
    def resume(self):
        """Resume the stopwatch"""
        if self._pause_time is not None:
            self._paused_duration += time.time() - self._pause_time
            self._pause_time = None
    
    def reset(self):
        """Reset the stopwatch to zero"""
        self._start_time = time.time()
        self._pause_time = None
        self._paused_duration = 0


def wait(time_ms: int):
    """
    Wait for a specified amount of time.
    
    Args:
        time_ms: Time to wait in milliseconds
    """
    time.sleep(time_ms / 1000.0)


class DataLog:
    """
    Simple data logger (stub for compatibility)
    
    In the real pybricks, this logs data to a file.
    For the emulator, we'll just print to console.
    """
    
    def __init__(self, *headers):
        """Initialize with column headers"""
        self.headers = headers
        print(f"DataLog initialized with headers: {headers}")
    
    def log(self, *values):
        """Log a row of data"""
        # In emulator, just ignore or print if needed
        pass

