from config.ports import PORTS
from pybricks.ev3devices import Motor

class PowerTrain:
    _instance = None
    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        instance = super().__new__(cls)
        cls._instance = instance
        return instance
        
    def __init__(self):
        self.port_left = PORTS["LEFT_MOTOR"]
        self.port_right = PORTS["RIGHT_MOTOR"]

        print("Setting up left motor on port:", self.port_left)
        self.left = Motor(self.port_left)

        print("Setting up right motor on port:", self.port_right)
        self.right = Motor(self.port_right)

    def move_forward(self, speed):
        self.left.run(speed)
        self.right.run(speed)

    def stop(self):
        self.left.stop()
        self.right.stop()
