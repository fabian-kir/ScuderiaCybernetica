class DriveBase:
	def __init__(self, left_motor, right_motor, wheel_diameter=56, axle_track=114):
		self.left_motor = left_motor
		self.right_motor = right_motor
		self._distance_mm = 0.0
		self._speed = 0.0
		self._turn_rate = 0.0

	def settings(self, straight_speed, straight_accel, turn_rate, turn_accel):
		# No-op for emulator
		return

	def reset(self):
		self._distance_mm = 0.0

	def distance(self) -> int:
		return int(self._distance_mm)

	def drive(self, speed_mm_s: float, turn_rate_deg_s: float):
		# Update motors roughly proportional to speed
		self._speed = speed_mm_s
		self._turn_rate = turn_rate_deg_s
		# Just forward power mapping for visibility
		pwr = max(-100, min(100, speed_mm_s / 10.0))
		self.left_motor.dc(pwr)
		self.right_motor.dc(pwr)
		# We don't integrate distance over time here; hardware wrappers will call periodically
		return


