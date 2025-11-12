CONSTANTS = {
    "WHEEL_DIAMETER": 57,
    "AXLE_TRACK": 120,
    "GEAR_RATIO_BALANCE_X": 1/1,
    "GEAR_RATIO_BALANCE_Y": 1/1,
    "DEFAULT_SPEED_BALANCE_X": 50,
    "DEFAULT_SPEED_BALANCE_Y": 50,
    "X_DISTANCE_AXLE_SLEDS": 500, # in mm
    "POWER_PER_SPEED": 30, # this is the best estimate for d (dc) / d s (for dc is power output and s is speed in mm/s)
    
    # PI speed controller gains for drive motor
    # KP: proportional gain (power per speed error in deg/s)
    # KI: integral gain (power per speed error per second)
    "DRIVE_SPEED_KP": 1.0,  # Start conservative, tune up if response is slow
    "DRIVE_SPEED_KI": 0.2,  # Start low, tune up if steady-state error persists
    
    # Speed filtering (first-order IIR filter)
    # alpha: 0..1, higher = less filtering (more responsive, more noise)
    "SPEED_FILTER_ALPHA": 0.3,
    
    # Braking parameters
    "BRAKE_K": 0.8,  # Brake duty cycle scaling factor (0.3..1.2 typical)
    "BRAKE_PULSE_MS": 80,  # Duration of reverse brake pulse in milliseconds (50..150 typical)
    
    # Stop detection threshold
    "STOP_SPEED_THRESHOLD": 5,  # Speed threshold in deg/s below which motor is considered stopped
}