"""
Utility modules for robot software.
"""

from software_ev3.utils.data_logger import DataLogger
from software_ev3.config.constants import CONSTANTS

# Convenience instance for easy access
# Usage: from utils import logger; logger.log_data(...)
# Logging can be disabled via CONSTANTS.DATA_LOGGING_ENABLED
logger = DataLogger(enabled=CONSTANTS.DATA_LOGGING_ENABLED)
