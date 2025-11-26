"""
Robot configuration constants.

This module contains all tunable parameters for the robot's hardware and control systems.
Constants are organized by subsystem for better maintainability.
"""

class CONSTANTS:
    CALIBRATE_ON_START = True # set this to false to use the stored calibration data of the last run
    PATH_TO_CALIBRATION_DATA = "software_ev3/config/calibration_data_0deg.csv"
    DRIVE_MOTOR_SLOPE_CALIBRATION_CSV_PATH  = "software_ev3/config/drive_motor_slope_calibration.csv"

    ULTRASONIC_PENDULUM_LENGTH = 155 # in mm
    
    # Data logging: set to False to disable all file logging (improves performance)
    DATA_LOGGING_ENABLED = False

    TIME_UNTIL_PLATFORM_CONTROLLER_STARTS = 0 # in Seconds

    # Gear ratios for balance platform motors
    GEARS_PLATFORM_FORWARD = [24, 56]
    GEARS_PLATFORM_SIDEWAYS = [[12, 20], [8, 40]]

    # Motors need to go at a minimum speed so that there's no wiggle
    MIN_SPEED_PLATFORM_FORWARD = 2

    # Proportional gain: angle correction per unit of reflection error
    # Higher values = faster response
    PLATFORM_FORWARD_MAX_SPEED = 80
    PLATFORM_FORWARD_SPEED_KP = 1

    PLATFORM_SIDEWAYS_SPEED_KP = -5
    MIN_SPEED_PLATFORM_SIDEWAYS = 5
    PLATFORM_SIDEWAYS_MAX_SPEED = 60

    MOTOR_FORWARD_MAX_DEGREE = 80 # max rotation from calibration-0
    MOTOR_SIDEWAYS_MAX_DEGREE = 40

    # DRIVE MOTOR

    GEARS_DRIVE_MOTOR = [1, ]
    DRIVE_MOTOR_TARGET_SPEED = 300
    DRIVE_MOTOR_MAX_SPEED = 2000 # in deg / s

    DRIVE_MOTOR_MIN_POWER = .5 # in V

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