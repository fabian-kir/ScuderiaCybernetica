"""
Pybricks media.ev3dev module emulation

Contains sound files and fonts for the EV3.
"""

from ...emulator_state import emulator_state


class SoundFile:
    """Sound file constants"""
    HELLO = "HELLO"
    GOODBYE = "GOODBYE"
    FANFARE = "FANFARE"
    ERROR_ALARM = "ERROR_ALARM"
    START = "START"
    STOP = "STOP"
    OBJECT = "OBJECT"
    OUCH = "OUCH"
    BLIP_1 = "BLIP_1"
    BLIP_2 = "BLIP_2"
    BLIP_3 = "BLIP_3"
    BLIP_4 = "BLIP_4"
    GO = "GO"
    BACKING_ALERT = "BACKING_ALERT"
    HORN_1 = "HORN_1"
    HORN_2 = "HORN_2"
    LASER = "LASER"
    SONAR = "SONAR"
    MOTOR_IDLE = "MOTOR_IDLE"
    MOTOR_START = "MOTOR_START"
    MOTOR_STOP = "MOTOR_STOP"
    CLICK = "CLICK"
    CONFIRM = "CONFIRM"
    GENERAL_ALERT = "GENERAL_ALERT"
    OVERPOWER = "OVERPOWER"


class ImageFile:
    """Image file constants (for display)"""
    RIGHT = "RIGHT"
    FORWARD = "FORWARD"
    LEFT = "LEFT"
    BACKWARD = "BACKWARD"
    STOP_1 = "STOP_1"
    STOP_2 = "STOP_2"
    
    # Many more image files exist in real pybricks
    # Add as needed


class Font:
    """
    Font for the EV3 screen
    
    Args:
        family: Font family (not used in emulator)
        size: Font size in pixels
        bold: Whether to use bold
        monospace: Whether to use monospace
        lang: Language (not used in emulator)
        script: Script (not used in emulator)
    """
    
    def __init__(self, family=None, size=12, bold=False, monospace=False, lang=None, script=None):
        self.family = family
        self.size = size
        self.bold = bold
        self.monospace = monospace
        self.lang = lang
        self.script = script
    
    def __repr__(self):
        return f"Font(size={self.size}, bold={self.bold})"

