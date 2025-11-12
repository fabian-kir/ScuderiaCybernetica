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
	LEFT = "LEFT"
	RIGHT = "RIGHT"
	UP = "UP"
	DOWN = "DOWN"
	CENTER = "MIDDLE"
	MIDDLE = "MIDDLE"


class Stop(Enum):
	COAST = "COAST"
	BRAKE = "BRAKE"
	HOLD = "HOLD"


