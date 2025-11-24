"""
Pybricks parameters module emulation

Contains all the constants and enums used by pybricks.
"""

from enum import Enum


class Port:
    """Motor and sensor ports"""
    # Motor ports
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    
    # Sensor ports
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class Button(Enum):
    """EV3 Brick buttons"""
    LEFT_DOWN = "LEFT_DOWN"
    DOWN = "DOWN"
    RIGHT_DOWN = "RIGHT_DOWN"
    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"
    LEFT_UP = "LEFT_UP"
    UP = "UP"
    RIGHT_UP = "RIGHT_UP"


class Color(Enum):
    """Standard colors"""
    BLACK = "BLACK"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    WHITE = "WHITE"
    BROWN = "BROWN"
    ORANGE = "ORANGE"
    PURPLE = "PURPLE"


class Stop(Enum):
    """Motor stop types"""
    COAST = "COAST"
    BRAKE = "BRAKE"
    HOLD = "HOLD"


class Direction(Enum):
    """Motor rotation directions"""
    CLOCKWISE = "CLOCKWISE"
    COUNTERCLOCKWISE = "COUNTERCLOCKWISE"

