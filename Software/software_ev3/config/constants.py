"""
Robot configuration constants.

This module contains all tunable parameters for the robot's hardware and control systems.
Constants are organized by subsystem for better maintainability.
"""

CONSTANTS = {
    # ============================================================================
    # Platform/Balance Motor Configuration
    # ============================================================================
    # Gear ratios for balance platform motors
    # Applied to angle commands: actual_motor_angle = command_angle * gear_ratio
    "GEAR_RATIO_BALANCE_X": -3,  # Gear ratio for X-axis balance motor
    "GEAR_RATIO_BALANCE_Y": 1/1,  # Gear ratio for Y-axis balance motor
    
    # Default speeds for balance platform motors (deg/s)
    # Used when no speed is explicitly specified in move_plattform()
    "DEFAULT_SPEED_BALANCE_X": 50,  # Default speed for X-axis motor
    "DEFAULT_SPEED_BALANCE_Y": 50,  # Default speed for Y-axis motor
    
    # ============================================================================
    # Platform Balance PID Controller Configuration
    # ============================================================================
    # PID gains for color sensor-based platform balance (X-axis)
    # Proportional gain: angle correction per unit of reflection error
    # Higher values = faster response but may cause overshoot/oscillation
    # Units: degrees per reflection error unit
    # Typical range: 0.1 - 1.0
    "PLATFORM_COLOR_KP": 1,
    
    # Integral gain: angle correction per unit of reflection error per second
    # Eliminates steady-state error but can cause windup if too high
    # Units: degrees per reflection error unit per second
    # Typical range: 0.01 - 0.1
    "PLATFORM_COLOR_KI": 0.05,
    
    # Derivative gain: angle correction per unit of reflection error rate
    # Dampens oscillations and improves stability
    # Units: degrees per reflection error rate unit
    # Typical range: 0.001 - 0.2
    "PLATFORM_COLOR_KD": 0.005,
    
    # PID gains for ultrasonic sensor-based platform balance (Y-axis)
    # Proportional gain: angle correction per unit of distance error (mm)
    # Higher values = faster response but may cause overshoot/oscillation
    # Units: degrees per millimeter of distance error
    # Typical range: 0.01 - 0.1
    "PLATFORM_ULTRASONIC_KP": 0.05,
    
    # Integral gain: angle correction per unit of distance error per second
    # Eliminates steady-state error but can cause windup if too high
    # Units: degrees per millimeter of distance error per second
    # Typical range: 0.001 - 0.01
    "PLATFORM_ULTRASONIC_KI": 0.005,
    
    # Derivative gain: angle correction per unit of distance error rate
    # Dampens oscillations and improves stability
    # Units: degrees per millimeter per second of distance error rate
    # Typical range: 0.001 - 0.02
    "PLATFORM_ULTRASONIC_KD": 0.005,
    
    # Maximum speed limits for platform balance corrections (deg/s)
    # Prevents sudden movements that could impart impulse to objects on platform
    # Lower values = smoother but slower response
    # Higher values = faster response but risk of impulse
    "PLATFORM_MAX_SPEED_X": 40,  # Maximum speed for X-axis corrections
    "PLATFORM_MAX_SPEED_Y": 50,  # Maximum speed for Y-axis corrections
    
    # Maximum angle correction per update cycle (degrees)
    # Additional safety limit to prevent large corrections in single step
    "PLATFORM_MAX_ANGLE_CORRECTION_X": 10,  # Maximum angle correction for X-axis per update
    "PLATFORM_MAX_ANGLE_CORRECTION_Y": 2.0,  # Maximum angle correction for Y-axis per update
    
    # Integral windup prevention limits
    # Maximum accumulated integral error to prevent windup
    "PLATFORM_MAX_INTEGRAL_X": 50.0,  # Maximum integral accumulation for X-axis
    "PLATFORM_MAX_INTEGRAL_Y": 50.0,  # Maximum integral accumulation for Y-axis

    "CORRECTION_ERROR_TRESHOLD": 0, # Amount of Value difference for the sensor so that the controller starts to move the plattform
    
    # ============================================================================
    # Drive Motor PID Controller Configuration
    # ============================================================================
    # Proportional gain: power output per speed error
    # Higher values = faster response but may cause overshoot/oscillation
    "DRIVE_SPEED_KP": .1,
    
    # Integral gain: power output per speed error per second
    # Eliminates steady-state error but can cause windup if too high
    "DRIVE_SPEED_KI": 0.1,

    # Derivative gain:
    "DRIVE_SPEED_KD": 0.1,

    """
    K_p 0.1 → 10 Start small; increase until system responds quickly but doesn’t overshoot too much.
    K_i 0.01 → 1 Usually smaller than K_p; increase slowly to remove steady-state error.
    K_d 0 → 1 Typically smallest; helps stabilize oscillations. Start with 0 and add only if needed.
    """
    
    # Speed compensation factor for slope compensation
    # How much to increase target speed per unit of resistance increase
    # Higher resistance (uphill) = higher target speed to maintain constant velocity
    # Units: deg/s per resistance unit
    # Typical range: 10.0 - 30.0
    "SPEED_COMPENSATION_PER_RESISTANCE": 20.0,
    "DRIVE_MOTOR_BASE_RESISTANCE": .0001, # the resistance the drive motor experiences when just going straight
                                          # and not uphill - needs to be adjusted when robots weight changes
}