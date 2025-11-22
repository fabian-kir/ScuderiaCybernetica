class PIDController:
    def __init__(self, kp, ki, kd, get_state, max_i=None, target_value=0.0):
        assert kp >= 0 and ki >= 0 and kd >= 0, "PID coefficients must be non-negative."

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.get_state = get_state
        self.target_value = target_value

        self.max_i = max_i

        self._integral = 0.0
        self._prev_error = None

    def __call__(self, dt, error=None):
        if error is None:
            current_value = self.get_state()
            error = self.target_value - current_value

        if self._prev_error is None:
            self._prev_error = error

        # Proportional term
        p_term = self.kp * error

        # Integral term with clamping and time delta
        self._integral += error * dt
        if self.max_i is not None:
            self._integral = max(min(self._integral, self.max_i), -self.max_i)
        i_term = self.ki * self._integral

        # Derivative term with time delta
        d_term = self.kd * (error - self._prev_error) / dt
        self._prev_error = error

        return p_term + i_term + d_term

    def set_target(self, target):
        self.target_value = target

    def reset(self):
        self._integral = 0.0
        self._prev_error = None

    def get_error(self):
        return self.target_value - self.get_state()
