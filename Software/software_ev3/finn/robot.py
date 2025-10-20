from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch, wait


class Robot:
    def __init__(self):
        """Konstruktor: erstellt alle Komponenten des Roboters."""
        # Hub initialisieren
        self.hub = EV3Brick()

        # Motoren
        self.left_motor = Motor(Port.A)
        self.right_motor = Motor(Port.D)
        self.balance_motor = Motor(Port.B)

        # DriveBase (für geradeaus / drehen)
        self.robot = DriveBase(
            self.left_motor,
            self.right_motor,
            wheel_diameter=57,
            axle_track=120
        )
        self.robot.settings(100, 100, 100, 100)

        # Sensoren
        self.color_left = ColorSensor(Port.S1)
        #self.distance_sensor = UltrasonicSensor(Port.S2)

        self.timer = StopWatch()
        self.last_distace = 0
        self.start_error = self.color_left.reflection()
        self.integral = 0



    def wallFollower(self, speed, distance, kp):
        self.robot.reset()
        wall_distance = 100

        while self.robot.distance() < distance :

            print(self.distance_sensor.distance())
            print(wall_distance - self.distance_sensor.distance())
            
            value = (wall_distance - self.distance_sensor.distance())*(-kp)
            value =max(-180, min(180, turn))
            self.robot.drive(speed, value) 
            self.balance(0.5)
            wait(100)
            

    def balance(self, ki):
        error = self.start_error - self.color_left.reflection()
        
        if abs(error) < 2 : 
            error = 0
        
        current_distance = self.robot.distance()
        ds = current_distance - self.last_distace

        self.integral = self.integral + error * ds

        self.last_distace = current_distance
        motor_angle = self.integral * ki

        self.balance_motor.run_target(100, motor_angle, then=Stop.COAST, wait = False)
        print( self.color_left.reflection(), error, self.integral)
        





        
