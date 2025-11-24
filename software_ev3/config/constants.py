"""
Robot configuration constants.

This module contains all tunable parameters for the robot's hardware and control systems.
Constants are organized by subsystem for better maintainability.
"""

class CONSTANTS:
    CALIBRATE_ON_START = True # set this to false to use the stored calibration data of the last run
    PATH_TO_CALIBRATION_DATA = "config/calibration_data_0deg.csv"
    DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH  = "config/drive_motor_slope_calibration.csv"

    TIME_UNTIL_PLATFORM_CONTROLLER_STARTS = 1 # in Seconds

    # Gear ratios for balance platform motors
    GEAR_RATIO_PLATFORM_FORWARD = -7
    GEAR_RATIO_PLATFORM_SIDEWAYS = 8.35

    # Motors need to go at a minimum speed so that there's no wiggle
    MIN_SPEED_PLATFORM_FORWARD = 25
    MIN_SPEED_PLATFORM_SIDEWAYS = 25

    # Proportional gain: angle correction per unit of reflection error
    # Higher values = faster response
    PLATFORM_FORWARD_MAX_SPEED = 1000
    PLATFORM_FORWARD_SPEED_KP = 50

    PLATFORM_SIDEWAYS_SPEED_KP = 50

    MOTOR_FORWARD_MAX_DEGREE = 20 # max rotation from calibration-0
    MOTOR_SIDEWAYS_MAX_DEGREE = 20

    # DRIVE MOTOR

    GEAR_RATIO_DRIVE_MOTOR = 1
    DRIVE_MOTOR_TARGET_SPEED = 300
    DRIVE_MOTOR_MAX_SPEED = 700 # in deg / s

    DRIVE_MOTOR_MIN_POWER = 2 # in V

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