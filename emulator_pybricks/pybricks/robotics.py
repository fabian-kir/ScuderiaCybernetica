"""
Pybricks robotics module emulation

Provides high-level robotics classes like DriveBase.
"""

from typing import Optional
from .ev3devices import Motor
from .parameters import Stop


class DriveBase:
    """
    Robot drive base with two wheels
    
    Provides simplified control for a differential drive robot.
    """
    
    def __init__(self, left_motor: Motor, right_motor: Motor, 
                 wheel_diameter: float, axle_track: float):
        """
        Initialize a drive base
        
        Args:
            left_motor: Left wheel motor
            right_motor: Right wheel motor
            wheel_diameter: Diameter of the wheels in mm
            axle_track: Distance between wheels in mm
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.wheel_diameter = wheel_diameter
        self.axle_track = axle_track
        
        # Calculate conversion factors
        import math
        self.wheel_circumference = math.pi * wheel_diameter
    
    def straight(self, distance: float, then: Stop = Stop.HOLD, wait: bool = True):
        """
        Drive straight for a specific distance
        
        Args:
            distance: Distance to drive in mm
            then: What to do after completing the movement
            wait: Whether to wait for completion
        """
        # Calculate rotation angle needed
        angle = (distance / self.wheel_circumference) * 360
        
        # Run both motors
        speed = 200  # Default speed
        self.left_motor.run_angle(speed, angle, then, wait=False)
        self.right_motor.run_angle(speed, angle, then, wait)
    
    def turn(self, angle: float, then: Stop = Stop.HOLD, wait: bool = True):
        """
        Turn in place by a specific angle
        
        Args:
            angle: Angle to turn in degrees
            then: What to do after completing the turn
            wait: Whether to wait for completion
        """
        # Calculate wheel rotation needed
        import math
        arc_length = (angle / 360) * (math.pi * self.axle_track)
        wheel_angle = (arc_length / self.wheel_circumference) * 360
        
        # Run motors in opposite directions
        speed = 200
        self.left_motor.run_angle(speed, wheel_angle, then, wait=False)
        self.right_motor.run_angle(speed, -wheel_angle, then, wait)
    
    def drive(self, drive_speed: float, turn_rate: float):
        """
        Drive at a specific speed and turn rate
        
        Args:
            drive_speed: Forward speed in mm/s
            turn_rate: Turn rate in degrees/s
        """
        # Convert to wheel speeds
        wheel_speed = (drive_speed / self.wheel_circumference) * 360
        turn_speed = (turn_rate / 360) * (self.axle_track / self.wheel_diameter) * 360
        
        left_speed = wheel_speed - turn_speed / 2
        right_speed = wheel_speed + turn_speed / 2
        
        self.left_motor.run(left_speed)
        self.right_motor.run(right_speed)
    
    def stop(self):
        """Stop both motors"""
        self.left_motor.stop()
        self.right_motor.stop()
    
    def distance(self) -> float:
        """
        Get the distance traveled
        
        Returns:
            Distance in mm
        """
        left_angle = self.left_motor.angle()
        right_angle = self.right_motor.angle()
        avg_angle = (left_angle + right_angle) / 2
        
        return (avg_angle / 360) * self.wheel_circumference
    
    def angle(self) -> float:
        """
        Get the angle turned
        
        Returns:
            Angle in degrees
        """
        left_angle = self.left_motor.angle()
        right_angle = self.right_motor.angle()
        diff_angle = (right_angle - left_angle) / 2
        
        import math
        return (diff_angle / 360) * (self.wheel_circumference / self.axle_track) * 360
    
    def state(self) -> tuple:
        """
        Get the current drive base state
        
        Returns:
            Tuple of (distance, drive_speed, angle, turn_rate)
        """
        # Simplified for emulator
        return (self.distance(), 0, self.angle(), 0)
    
    def reset(self):
        """Reset the driven distance and angle to zero"""
        self.left_motor.reset_angle(0)
        self.right_motor.reset_angle(0)

