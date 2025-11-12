from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MotorState:
	port: str
	power: float = 0.0
	speed: float = 0.0


@dataclass
class SensorState:
	port: str
	value: float = 0.0


class EmulatorState:
	def __init__(self):
		self._motors: Dict[str, MotorState] = {}
		self._sensors: Dict[str, SensorState] = {}
		self._buttons: Dict[str, bool] = {
			"LEFT": False,
			"RIGHT": False,
			"UP": False,
			"DOWN": False,
			"MIDDLE": False
		}

	def register_motor(self, port: str):
		self._motors.setdefault(port, MotorState(port))

	def set_motor(self, port: str, power: float = None, speed: float = None):
		m = self._motors.setdefault(port, MotorState(port))
		if power is not None:
			m.power = power
		if speed is not None:
			m.speed = speed

	def get_motors(self):
		return list(self._motors.values())

	def register_sensor(self, port: str, initial: float = 0.0):
		# Only register if port is valid
		if port and port != "None" and str(port) != "None":
			port_str = str(port)
			self._sensors.setdefault(port_str, SensorState(port_str, initial))

	def set_sensor(self, port: str, value: float):
		# Only set sensor if port is valid
		if port and port != "None" and str(port) != "None":
			s = self._sensors.setdefault(str(port), SensorState(str(port)))
			s.value = value

	def get_sensors(self):
		return list(self._sensors.values())

	def set_button(self, button_name: str, pressed: bool):
		if button_name in self._buttons:
			self._buttons[button_name] = pressed

	def is_button_pressed(self, button_name: str) -> bool:
		return self._buttons.get(button_name, False)

	def get_pressed_buttons(self) -> List[str]:
		return [name for name, pressed in self._buttons.items() if pressed]

	# Backward compatibility methods
	def set_button_middle(self, pressed: bool):
		self.set_button("MIDDLE", pressed)

	def is_button_middle(self) -> bool:
		return self.is_button_pressed("MIDDLE")


# Singleton
EMU_STATE = EmulatorState()
