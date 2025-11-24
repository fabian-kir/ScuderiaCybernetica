from enum import Enum


class Port(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class Button(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class Stop(Enum):
    COAST = "coast"
    BRAKE = "brake"
    HOLD = "hold"


__all__ = ["Port", "Button", "Stop"]

