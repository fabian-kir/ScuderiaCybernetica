from config.ports import PORTS
from config.constants import CONSTANTS
from pybricks.ev3devices import Motor

from utils.singleton import singleton


@singleton
class DriveMotor:
    """
    PID-controlled drive motor that maintains target speed in the horizontal plane.
    
    Automatically compensates for slope changes: when torque_per_power increases
    (going uphill), the controller increases power output proportionally to maintain
    the target horizontal speed.
    """
    
    def __init__(self):
        self.port = PORTS["DRIVE_MOTOR"]
        self.motor = Motor(self.port)
        self.motor.reset_angle(0)

        # Target speed (deg/s) - horizontal plane speed
        self.target_speed = 0
        
        # Current power output (-100 to 100)
        self.power = 0
        
        # PID controller state
        self._integral_error = 0.0
        self._previous_error = 0.0
        self._previous_speed = 0.0
        
        # Filtered speed for noise reduction
        self._filtered_speed = 0.0
        
        # Resistance/torque tracking for slope compensation
        self._current_resistance = CONSTANTS["BASE_RESISTANCE"]
        self._previous_power = 0.0

    def get_power(self):
        """Returns the current power output."""
        return self.power

    def get_torque_per_power(self):
        """
        Calculates the current torque-to-power ratio.
        
        Higher values indicate increased resistance (e.g., going uphill).
        Returns None if speed is zero to avoid division by zero.
        """
        current_speed = self.motor.speed()
        if abs(current_speed) < 1.0:  # Avoid division by zero
            return None
        
        # Torque per power = power / speed
        # When this increases, we're encountering more resistance
        return abs(self.power) / abs(current_speed) if current_speed != 0 else None

    def get_resistance(self):
        """
        Returns the current resistance estimate.
        Higher values indicate more resistance (uphill slope).
        """
        return self._current_resistance

    def drive(self, speed):
        """
        Sets the target speed for horizontal plane movement.
        
        Args:
            speed: Target speed in deg/s
        """
        self.target_speed = speed

    def update(self, dt):
        """
        Updates the PID controller and applies power to the motor.
        
        Args:
            dt: Time delta in seconds since last update
        """

        # Read current motor speed
        raw_speed = self.motor.speed()
        
        # Apply first-order IIR filter to reduce noise
        alpha = CONSTANTS["SPEED_FILTER_ALPHA"]
        self._filtered_speed = alpha * raw_speed + (1 - alpha) * self._filtered_speed
        
        # Calculate resistance based on torque_per_power ratio
        self._update_resistance()
        
        # Adjust target speed based on resistance (slope compensation)
        # When going uphill (higher resistance), increase target speed proportionally
        # to maintain constant horizontal velocity
        resistance_delta = self._current_resistance - CONSTANTS["BASE_RESISTANCE"]
        adjusted_target_speed = (
            self.target_speed + 
            resistance_delta * CONSTANTS["SPEED_COMPENSATION_PER_RESISTANCE"]
        )
        
        # Calculate speed error
        speed_error = adjusted_target_speed - self._filtered_speed
        
        # PID Controller
        # Proportional term
        proportional = CONSTANTS["DRIVE_SPEED_KP"] * speed_error
        '''
        # Integral term (with anti-windup)
        self._integral_error += speed_error * dt
        # Limit integral to prevent windup: clamp to [-max_integral, max_integral]
        max_integral = 100.0 / CONSTANTS["DRIVE_SPEED_KI"]
        self._integral_error = max(-max_integral, min(max_integral, self._integral_error))
        integral = CONSTANTS["DRIVE_SPEED_KI"] * self._integral_error
        
        # Derivative term (rate of change of error)
        error_derivative = (speed_error - self._previous_error) / dt if dt > 0.0 else 0.0
        # Use KD if available, otherwise 0
        kd = CONSTANTS.get("DRIVE_SPEED_KD", 0.0)
        derivative = kd * error_derivative'''
        
        # Calculate total power output
        self.power = proportional #+ integral + derivative
        
        # Clamp power to valid range [-100, 100]
        self.power = max(-100, min(100, self.power))

        # Apply power to motor
        self.motor.dc(self.power)
        
        # Update state for next iteration
        self._previous_error = speed_error
        self._previous_power = self.power
        self._previous_speed = self._filtered_speed

    def _update_resistance(self):
        """
        Updates the resistance estimate based on current torque_per_power ratio.
        
        Higher resistance indicates uphill slope, requiring more power for the same speed.
        """
        torque_per_power = self.get_torque_per_power()
        
        if torque_per_power is not None:
            # Update resistance estimate using exponential moving average
            # Higher torque_per_power = higher resistance
            resistance_alpha = 0.3  # Smoothing factor for resistance updates
            estimated_resistance = torque_per_power
            self._current_resistance = (
                resistance_alpha * estimated_resistance + 
                (1 - resistance_alpha) * self._current_resistance
            )
        else:
            # If we can't calculate (e.g., stopped), gradually return to base resistance
            decay_rate = 0.95
            self._current_resistance = (
                decay_rate * self._current_resistance + 
                (1 - decay_rate) * CONSTANTS["BASE_RESISTANCE"]
            )