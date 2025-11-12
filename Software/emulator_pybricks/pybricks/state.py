from dataclasses import dataclass, field
from typing import Dict, List
import time


@dataclass
class MotorState:
	port: str
	power: float = 0.0
	speed: float = 0.0
	angle: float = 0.0
	target_speed: float = 0.0  # Speed set by run() - used for angle integration
	last_update_time: float = field(default_factory=time.perf_counter)
	using_run_mode: bool = False  # True when run() is used, False when dc() is used
	# Background command tracking (for wait=False operations)
	target_angle: float = None  # Target angle for run_angle/run_target (None if not active)
	target_time_end: float = None  # End time for run_time (None if not active)
	command_then: object = None  # Stop behavior to apply when command completes
	command_start_angle: float = 0.0  # Angle when command started (for run_angle)
	command_start_time: float = 0.0  # Time when command started (for run_time)


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

	def set_motor(self, port: str, power: float = None, speed: float = None, angle: float = None, 
	              target_speed: float = None, using_run_mode: bool = None,
	              target_angle: float = None, target_time_end: float = None,
	              command_then: object = None, command_start_angle: float = None,
	              command_start_time: float = None, clear_command: bool = False):
		m = self._motors.setdefault(port, MotorState(port))
		current_time = time.perf_counter()
		
		# Integrate angle BEFORE updating parameters
		# Use the current target_speed for the elapsed time period
		if m.using_run_mode:
			dt = current_time - m.last_update_time
			if dt > 0:
				# Integrate speed over time: angle += speed * dt
				# Speed is in degrees per second (typical Pybricks units)
				new_angle = m.angle + m.target_speed * dt
				
				# Check if we have a target angle and would overshoot
				if m.target_angle is not None:
					if m.target_angle >= m.command_start_angle:
						# Moving forward - clamp to target
						if new_angle > m.target_angle:
							new_angle = m.target_angle
					else:
						# Moving backward - clamp to target
						if new_angle < m.target_angle:
							new_angle = m.target_angle
				
				m.angle = new_angle
		
		# Check if background command has completed (before updating parameters)
		completed_command_info = self._check_command_completion(m, current_time)
		
		# Now update parameters
		if power is not None:
			m.power = power
		if speed is not None:
			m.speed = speed
		if angle is not None:
			m.angle = angle
		if target_speed is not None:
			m.target_speed = target_speed
		if using_run_mode is not None:
			m.using_run_mode = using_run_mode
		if target_angle is not None:
			m.target_angle = target_angle
		if target_time_end is not None:
			m.target_time_end = target_time_end
		if command_then is not None:
			m.command_then = command_then
		if command_start_angle is not None:
			m.command_start_angle = command_start_angle
		if command_start_time is not None:
			m.command_start_time = command_start_time
		if clear_command:
			m.target_angle = None
			m.target_time_end = None
			m.command_then = None
		
		m.last_update_time = current_time
		
		# Return completion info for Motor class to handle
		return completed_command_info
	
	def _check_command_completion(self, m: MotorState, current_time: float):
		"""Check if a background motor command has completed. Returns (completed, then_behavior) or None."""
		command_completed = False
		
		if m.target_angle is not None:
			# Check if we've reached the target angle
			angle_reached = False
			if m.target_angle >= m.command_start_angle:
				# Moving forward
				angle_reached = m.angle >= m.target_angle
			else:
				# Moving backward
				angle_reached = m.angle <= m.target_angle
			
			if angle_reached:
				command_completed = True
		
		if m.target_time_end is not None:
			# Check if time has elapsed
			if current_time >= m.target_time_end:
				command_completed = True
		
		if command_completed:
			then_behavior = m.command_then
			# Ensure angle is exactly at target (no overshoot)
			if m.target_angle is not None:
				m.angle = m.target_angle
			# Stop the motor immediately to prevent overshoot
			# But keep using_run_mode=True so angle tracking continues to work
			# Only dc() should set using_run_mode=False
			m.target_speed = 0.0
			m.power = 0.0
			m.speed = 0.0
			# Clear the command (but angle stays at reached value)
			m.target_angle = None
			m.target_time_end = None
			m.command_then = None
			return (True, then_behavior)
		
		return None

	def get_motors(self):
		# Update angles for all motors before returning
		current_time = time.perf_counter()
		for m in self._motors.values():
			if m.using_run_mode:
				dt = current_time - m.last_update_time
				if dt > 0:
					# Integrate angle with overshoot prevention
					new_angle = m.angle + m.target_speed * dt
					
					# Check if we have a target angle and would overshoot
					if m.target_angle is not None:
						if m.target_angle >= m.command_start_angle:
							# Moving forward - clamp to target
							if new_angle > m.target_angle:
								new_angle = m.target_angle
						else:
							# Moving backward - clamp to target
							if new_angle < m.target_angle:
								new_angle = m.target_angle
					
					m.angle = new_angle
					m.last_update_time = current_time
				# Check for command completion
				self._check_command_completion(m, current_time)
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
