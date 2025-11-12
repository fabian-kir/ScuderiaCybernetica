import warnings

from pybricks.robotics import DriveBase

from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor
from pybricks.tools import wait

from utils.singleton import singleton
from hardware.robot_hub import RobotHub

@singleton
class DriveMotor:
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]

        self.motor = Motor(self.port)
        self.motor.reset_angle(0)

        self.base_target_speed = 0  # Base target speed set by drive()
        self.target_speed = 0  # Adjusted target speed (base + resistance compensation)
        self.power = 0
        self.power_per_speed = CONSTANTS["POWER_PER_SPEED"]

        # Closed-loop PI speed controller gains and state
        self.kp = CONSTANTS["DRIVE_SPEED_KP"]   # proportional gain (power per speed error)
        self.ki = CONSTANTS["DRIVE_SPEED_KI"]  # integral gain (power per speed error per second)
        self.integral = 0.0

        # Power output limits for EV3 dc(): [-100, 100]
        self.power_min, self.power_max = -100, 100

        self._last_speed = 0
        
        # Resistance compensation parameters
        self.speed_compensation_per_resistance = CONSTANTS.get("SPEED_COMPENSATION_PER_RESISTANCE", 5.0)
        self.base_resistance = CONSTANTS.get("BASE_RESISTANCE", 2.0)

        RobotHub().print("Set up drive motor on port:", self.port)

    def _get_current_resistance(self):
        """Get current motor resistance from emulator state, or return base resistance."""
        try:
            # Try to import EMU_STATE from emulator (only available in emulator mode)
            from pybricks.state import EMU_STATE
            motors = EMU_STATE.get_motors()
            port_str = str(self.port)
            for m in motors:
                if str(m.port) == port_str:
                    return m.resistance
            return self.base_resistance
        except (ImportError, AttributeError):
            # Not in emulator mode or EMU_STATE not available
            return self.base_resistance
    
    def _update_target_speed_with_resistance_compensation(self):
        """Update target speed based on current resistance to maintain constant velocity."""
        current_resistance = self._get_current_resistance()
        resistance_delta = current_resistance - self.base_resistance
        # Linear compensation: higher resistance = higher target speed
        speed_adjustment = resistance_delta * self.speed_compensation_per_resistance
        self.target_speed = self.base_target_speed + speed_adjustment

    def update(self, dt):
        # Update target speed based on current resistance
        self._update_target_speed_with_resistance_compensation()
        
        # Read speed and compute error (target - actual)
        raw_speed = self.motor.speed()

        # simple first-order IIR filter to reduce noise on speed estimate
        alpha = CONSTANTS.get("SPEED_FILTER_ALPHA", 0.3)  # 0..1, higher = less filtering
        speed = alpha * raw_speed + (1 - alpha) * self._last_speed
        self._last_speed = speed

        error = self.target_speed - speed

        # Integrate error using dt (seconds). Protect against None/zero dt.
        dt = max(1e-3, float(dt))  # avoid division by zero and ensure numeric

        # Provisional integral update
        new_integral = self.integral + error * dt

        # Unsaturated PI control signal (power command)
        u_unsat = self.kp * error + self.ki * new_integral

        # Saturate to valid dc() range
        u = max(self.power_min, min(self.power_max, u_unsat))

        # Anti-windup: only accept integral update if we are not driving further into saturation
        pushing_further_into_sat = (
            (u == self.power_max and u_unsat > u) or
            (u == self.power_min and u_unsat < u)
        )
        if not pushing_further_into_sat:
            self.integral = new_integral  # accept the integral step

        # Apply power
        self.power = u
        self.motor.dc(int(self.power))

    def drive(self, speed, slope=0):
        self.base_target_speed = speed
        # Update target speed with resistance compensation
        self._update_target_speed_with_resistance_compensation()
        # Reset integral to prevent windup when changing targets
        self.integral = 0.0
        # Note: slope parameter is reserved for future use (e.g., acceleration limiting)

    def stop(self, brake_motors=True, hold_after=True, timeout_ms=600):
        # Request zero speed
        self.base_target_speed = 0
        self.target_speed = 0

        # Optionally apply a short reverse pulse to actively brake
        if brake_motors:
            v = abs(self.motor.speed())
            # Duty scaled to current speed with safe bounds
            k = CONSTANTS.get("BRAKE_K", 0.8)  # tune 0.3..1.2
            duty = int(max(0, min(100, k * v)))
            pulse_ms = CONSTANTS.get("BRAKE_PULSE_MS", 80)  # 50..150 typical

            self.motor.dc( -duty )
            wait(pulse_ms)
            self.motor.dc(0)

        # Optionally hold position once near standstill
        if hold_after:
            # Avoid busy-wait; poll with a small sleep and a timeout
            threshold = int(CONSTANTS.get("STOP_SPEED_THRESHOLD", 5))  # deg/s
            elapsed = 0
            step = 20  # ms
            while elapsed < timeout_ms:
                if abs(self.motor.speed()) <= threshold:
                    break
                wait(step)
                elapsed += step
            self.motor.hold()

    def get_power(self):
        return self.power

    def get_torque_per_speed(self):
        return self.power_per_speed