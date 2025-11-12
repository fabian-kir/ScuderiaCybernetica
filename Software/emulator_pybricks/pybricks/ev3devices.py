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

	def reset_angle(self, angle: float):
		# Update angle integration before resetting
		motors = EMU_STATE.get_motors()
		for m in motors:
			if m.port == self._port:
				# Trigger angle update by calling set_motor with current values
				EMU_STATE.set_motor(self._port, power=m.power, speed=m.speed,
				                    target_speed=m.target_speed, using_run_mode=m.using_run_mode)
				break
		# Now reset the angle
		EMU_STATE.set_motor(self._port, angle=angle)
		process_ui_events()

	def run(self, speed: float):
		# Clamp and set target speed for angle integration
		target_speed = max(-100.0, min(100.0, float(speed)))
		self._speed = target_speed
		# crude speed model follows power
		self._speed += (self._power * 2.0 - self._speed) * 0.3
		# Use run mode: we can track angle by integrating speed
		# Clear any active background commands when starting a new run command
		result = EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed, 
		                    target_speed=target_speed, using_run_mode=True,
		                    clear_command=True)
		self._handle_command_completion(result)
		process_ui_events()

	def dc(self, power: float):
		# Clamp and set
		self._power = max(-100.0, min(100.0, float(power)))
		# crude speed model follows power
		self._speed += (self._power * 2.0 - self._speed) * 0.3
		# Use dc mode: we cannot track angle accurately (no target speed)
		# Clear any active background commands when using dc()
		result = EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed,
		                    target_speed=0.0, using_run_mode=False, clear_command=True)
		self._handle_command_completion(result)
		process_ui_events()

	def speed(self) -> float:
		# return current emulated speed
		# Check for command completion while processing events
		process_ui_events()
		# Also check when reading speed
		motors = EMU_STATE.get_motors()
		for m in motors:
			if m.port == self._port:
				result = EMU_STATE.set_motor(self._port, power=m.power, speed=m.speed,
				                    target_speed=m.target_speed, using_run_mode=m.using_run_mode)
				self._handle_command_completion(result)
				break
		return self._speed

	def angle(self) -> float:
		# Return current angle (only accurate when using run(), not dc())
		process_ui_events()
		# Update angle integration before reading and check for command completion
		motors = EMU_STATE.get_motors()
		for m in motors:
			if m.port == self._port:
				# Trigger angle update by calling set_motor with current values
				result = EMU_STATE.set_motor(self._port, power=m.power, speed=m.speed,
				                    target_speed=m.target_speed, using_run_mode=m.using_run_mode)
				self._handle_command_completion(result)
				return m.angle
		return 0.0
	
	def _handle_command_completion(self, completion_info):
		"""Handle completed background motor commands by applying the 'then' behavior."""
		if completion_info is None:
			return
		
		completed, then_behavior = completion_info
		if completed and then_behavior is not None:
			from .parameters import Stop
			if then_behavior == Stop.HOLD or (hasattr(then_behavior, 'value') and then_behavior.value == "HOLD"):
				self.hold()
			elif then_behavior == Stop.COAST or (hasattr(then_behavior, 'value') and then_behavior.value == "COAST"):
				self.stop()
			elif then_behavior == Stop.BRAKE or (hasattr(then_behavior, 'value') and then_behavior.value == "BRAKE"):
				self.brake()

	def run_angle(self, speed: float, rotation_angle: float, then=None, wait=True):
		"""Run motor at specified speed by a given angle.
		
		According to Pybricks API: Runs the motor at a constant speed by a given angle.
		The motor accelerates to the given speed, keeps running at this speed, and then decelerates.
		"""
		from .tools import wait as wait_func
		from .parameters import Stop
		import time
		
		# Validate inputs
		if speed is None:
			raise ValueError("speed cannot be None")
		if rotation_angle is None:
			raise ValueError("rotation_angle cannot be None")
		
		speed = float(speed)
		rotation_angle = float(rotation_angle)
		
		# Get current angle (this also updates integration)
		current_angle = self.angle()
		target_angle = current_angle + rotation_angle
		
		# Determine direction - speed sign should match rotation direction
		if rotation_angle < 0:
			actual_speed = -abs(speed)
		else:
			actual_speed = abs(speed)
		
		# Default "then" behavior is HOLD if not specified
		if then is None:
			then = Stop.HOLD
		
		if wait:
			# Start running at specified speed
			self.run(actual_speed)
			
			# Wait until target angle is reached
			# Use a small tolerance to account for integration precision
			tolerance = 1.0  # degrees
			while True:
				current = self.angle()
				if rotation_angle >= 0:
					if current >= target_angle - tolerance:
						break
				else:
					if current <= target_angle + tolerance:
						break
				wait_func(10)  # Small delay to avoid busy-waiting
			
			# Apply "then" behavior
			if then == Stop.HOLD or (hasattr(then, 'value') and then.value == "HOLD"):
				self.hold()
			elif then == Stop.COAST or (hasattr(then, 'value') and then.value == "COAST"):
				self.stop()
			elif then == Stop.BRAKE or (hasattr(then, 'value') and then.value == "BRAKE"):
				self.brake()
		else:
			# Background mode: start running and track target
			# Start running at specified speed
			self.run(actual_speed)
			
			# Set up background tracking
			EMU_STATE.set_motor(self._port, 
			                    target_angle=target_angle,
			                    command_then=then,
			                    command_start_angle=current_angle)
			process_ui_events()

	def run_target(self, speed: float, target_angle: float, then=None, wait=True):
		"""Run motor at specified speed towards a given target angle.
		
		According to Pybricks API: Runs the motor at a constant speed towards a given target angle.
		The direction of rotation is automatically selected based on the target angle.
		"""
		current_angle = self.angle()
		angle_diff = target_angle - current_angle
		self.run_angle(speed, angle_diff, then=then, wait=wait)
	
	def run_time(self, speed: float, time_ms: float, then=None, wait=True):
		"""Run motor at specified speed for a given amount of time.
		
		According to Pybricks API: Runs the motor at a constant speed for a given amount of time.
		The motor accelerates to the given speed, keeps running at this speed, and then decelerates.
		"""
		from .tools import wait as wait_func
		from .parameters import Stop
		import time as time_module
		
		# Default "then" behavior is HOLD if not specified
		if then is None:
			then = Stop.HOLD
		
		# Start running at specified speed
		self.run(speed)
		
		start_time = time_module.perf_counter()
		end_time = start_time + (time_ms / 1000.0)  # Convert ms to seconds
		
		if wait:
			# Wait until time has elapsed
			while time_module.perf_counter() < end_time:
				wait_func(10)  # Small delay to avoid busy-waiting
			
			# Apply "then" behavior
			if then == Stop.HOLD or (hasattr(then, 'value') and then.value == "HOLD"):
				self.hold()
			elif then == Stop.COAST or (hasattr(then, 'value') and then.value == "COAST"):
				self.stop()
			elif then == Stop.BRAKE or (hasattr(then, 'value') and then.value == "BRAKE"):
				self.brake()
		else:
			# Background mode: track time target
			EMU_STATE.set_motor(self._port,
			                    target_time_end=end_time,
			                    command_then=then,
			                    command_start_time=start_time)
			process_ui_events()

	def stop(self):
		"""Stops the motor and lets it spin freely (coast).
		
		The motor gradually stops due to friction.
		"""
		self._power = 0.0
		self._speed = 0.0
		# stop() coasts, so angle tracking becomes inaccurate - disable it
		result = EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed,
		                    target_speed=0.0, using_run_mode=False, clear_command=True)
		self._handle_command_completion(result)
		process_ui_events()
	
	def brake(self):
		"""Passively brakes the motor.
		
		The motor stops due to friction, plus the voltage that is generated
		while the motor is still moving.
		"""
		self._power = 0.0
		self._speed = 0.0
		# brake() stops the motor, angle tracking becomes inaccurate - disable it
		result = EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed,
		                    target_speed=0.0, using_run_mode=False, clear_command=True)
		self._handle_command_completion(result)
		process_ui_events()

	def hold(self):
		"""Stops the motor and actively holds it at its current angle."""
		self._power = 0.0
		self._speed = 0.0
		# hold() actively holds position, so angle tracking should remain enabled
		# Keep using_run_mode=True so angle stays visible and accurate
		result = EMU_STATE.set_motor(self._port, power=self._power, speed=self._speed,
		                    target_speed=0.0, using_run_mode=True, clear_command=True)
		self._handle_command_completion(result)
		process_ui_events()


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


