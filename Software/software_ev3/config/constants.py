"""
Robot configuration constants.

This module contains all tunable parameters for the robot's hardware and control systems.
Constants are organized by subsystem for better maintainability.
"""

class CONSTANTS:
    # ============================================================================
    # Platform/Balance Motor Configuration
    # ============================================================================
    # Gear ratios for balance platform motors
    # Applied to angle commands: actual_motor_angle = command_angle * gear_ratio
    GEAR_RATIO_BALANCE_X = -3
    GEAR_RATIO_BALANCE_Y = 1/1

    # Default speeds for balance platform motors (deg/s)
    # Used when no speed is explicitly specified in move_plattform()
    DEFAULT_SPEED_BALANCE_X = 50
    DEFAULT_SPEED_BALANCE_Y = 50

    MAX_SPEED_BALANCE_X = 500
    MAX_SPEED_BALANCE_Y = 500

    # ============================================================================
    # Platform Balance Controller Configuration
    # ============================================================================
    # Proportional gain: angle correction per unit of reflection error
    # Higher values = faster response
    PLATFORM_COLOR_KP = 1


    # ============================================================================
    # Drive Motor PID Controller Configuration
    # ============================================================================
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

    # Speed compensation factor for slope compensation
    # How much to increase target speed per unit of resistance increase
    # Higher resistance (uphill) = higher target speed to maintain constant velocity
    # Units: deg/s per resistance unit
    # Typical range: 10.0 - 30.0
    SPEED_COMPENSATION_PER_RESISTANCE = 20.0
    DRIVE_MOTOR_BASE_RESISTANCE = .0001  # the resistance the drive motor experiences when just going straight
    # and not uphill - needs to be adjusted when robots weight changes