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
    "GEAR_RATIO_BALANCE_X": 1/1,  # Gear ratio for X-axis balance motor
    "GEAR_RATIO_BALANCE_Y": 1/1,  # Gear ratio for Y-axis balance motor
    
    # Default speeds for balance platform motors (deg/s)
    # Used when no speed is explicitly specified in move_plattform()
    "DEFAULT_SPEED_BALANCE_X": 50,  # Default speed for X-axis motor
    "DEFAULT_SPEED_BALANCE_Y": 50,  # Default speed for Y-axis motor
    
    # ============================================================================
    # Drive Motor PID Controller Configuration
    # ============================================================================
    # Proportional gain: power output per speed error (deg/s)
    # Higher values = faster response but may cause overshoot/oscillation
    # Typical range: 0.5 - 2.0
    "DRIVE_SPEED_KP": 1.0,
    
    # Integral gain: power output per speed error per second
    # Eliminates steady-state error but can cause windup if too high
    # Typical range: 0.1 - 0.5
    "DRIVE_SPEED_KI": 0.2,
    
    # ============================================================================
    # Drive Motor Speed Filtering
    # ============================================================================
    # First-order IIR filter coefficient for speed noise reduction
    # Range: 0.0 (maximum filtering, slow response) to 1.0 (no filtering, fast response)
    # Formula: filtered_speed = alpha * raw_speed + (1 - alpha) * previous_filtered_speed
    # Typical range: 0.2 - 0.5
    "SPEED_FILTER_ALPHA": 0.3,
    
    # ============================================================================
    # Drive Motor Slope/Resistance Compensation
    # ============================================================================
    # Reference resistance value representing flat ground conditions
    # Used as baseline for detecting uphill/downhill slopes
    # Units: torque_per_power ratio (dimensionless)
    "BASE_RESISTANCE": 2.0,
    
    # Speed compensation factor for slope compensation
    # How much to increase target speed per unit of resistance increase
    # Formula: adjusted_target_speed = base_target_speed + 
    #          (resistance - BASE_RESISTANCE) * SPEED_COMPENSATION_PER_RESISTANCE
    # Higher resistance (uphill) = higher target speed to maintain constant velocity
    # Units: deg/s per resistance unit
    # Typical range: 10.0 - 30.0
    "SPEED_COMPENSATION_PER_RESISTANCE": 20.0,
}