from .tools import wait
from .state import EMU_STATE
from .ui import process_ui_events


class Motor:
	def __init__(self, port):
		self._port = str(getattr(port, "value", port))
		EMU_STATE.register_motor(self._port)
		self._power = 0.0
		self._speed = 0.0
		process_ui_events()

	def run(self, speed: float):
		# Clamp and set
		self._speed = max(-100.0, min(100.0, float(speed)))
		# crude speed model follows power
		self._speed += (self._power * 2.0 - self._speed) * 0.3
		EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed)
		process_ui_events()

	def dc(self, power: float):
		# Clamp and set
		self._power = max(-100.0, min(100.0, float(power)))
		# crude speed model follows power
		self._speed += (self._power * 2.0 - self._speed) * 0.3
		EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed)
		process_ui_events()

	def speed(self) -> float:
		# return current emulated speed
		process_ui_events()
		return self._speed

	def hold(self):
		self._power = 0.0
		self._speed = 0.0
		EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed)
		process_ui_events()

	def stop(self):
		self.hold()


class UltrasonicSensor:
	def __init__(self, port):
		self._port = str(getattr(port, "value", port))
		EMU_STATE.register_sensor(self._port, initial=100.0)
		process_ui_events()

	def distance(self) -> float:
		# Return centimeters to match typical usage; project treats as generic number
		process_ui_events()
		for s in EMU_STATE.get_sensors():
			if s.port == self._port:
				return s.value
		return 0.0


class ColorSensor:
	def __init__(self, port):
		self._port = str(getattr(port, "value", port))
		EMU_STATE.register_sensor(self._port, initial=50.0)
		process_ui_events()

	def reflection(self) -> int:
		process_ui_events()
		for s in EMU_STATE.get_sensors():
			if s.port == self._port:
				return int(s.value)
		return 0


