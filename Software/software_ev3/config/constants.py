"""
Robot configuration constants.

This module contains all tunable parameters for the robot's hardware and control systems.
Constants are organized by subsystem for better maintainability.
"""

class CONSTANTS:
    RUN_NEW_CALIBRATION = True # set this to false to use the stored calibration data of the last run
    PATH_TO_CALIBRATION_DATA = "config/calibration_data_0deg.txt"

    # ============================================================================
    # Platform/Balance Motor Configuration
    # ============================================================================
    # Gear ratios for balance platform motors
    # Applied to angle commands: actual_motor_angle = command_angle * gear_ratio
    GEAR_RATIO_BALANCE_X = 3
    GEAR_RATIO_BALANCE_Y = 1

    # ============================================================================
    # Platform Balance Controller Configuration
    # ============================================================================
    # Proportional gain: angle correction per unit of reflection error
    # Higher values = faster response
    PLATFORM_X_KP = -5
    PLATFORM_Y_KP = 1

    MOTOR_X_MAX_DEGREE = 80 # max rotation from calibration-0 

    # ============================================================================
    # Drive Motor PID Controller Configuration
    # ============================================================================
    DRIVE_MOTOR_CONSTANT_POWER = 3 # in V

    DRIVE_MOTOR_MIN_POWER = 10

    # Proportional gain: power output per speed error
    # Higher values = faster response but may cause overshoot/oscillation
    DRIVE_MOTOR_KP = .1

    # Integral gain: power output per speed error per second
    # Eliminates steady-state error but can cause windup if too high
    DRIVE_MOTOR_KI = 0.03
    DRIVE_MOTOR_MAX_I = 80

    # Derivative gain:
    DRIVE_MOTOR_KD = 0.005

    # K_p 0.1 → 10 Start small; increase until system responds quickly but doesn’t overshoot too much.
    # K_i 0.01 → 1 Usually smaller than K_p; increase slowly to remove steady-state error.
    # K_d 0 → 1 Typically smallest; helps stabilize oscillations. Start with 0 and add only if needed.

    DRIVE_MOTOR_RESISTANCES_AVERAGING_STEPS = 20 # how many cycles the output of get_resistance will be averaged accross

    # AT 3V
    SLOPE_SPEED_ARRAY = [(421.78, -20), (400.00, -15), (379.1, -10), (346.46, -5), (296.6, 0), (250.76, 5), (210.64, 10), (165.38, 15), (102.34, 20)]