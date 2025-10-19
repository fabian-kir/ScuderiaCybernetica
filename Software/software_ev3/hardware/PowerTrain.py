from pybricks.ev3devices import Motor

class PowerTrain:
    def __init__(self, left_motor, right_motor):
        self.left = left_motor
        self.right = right_motor

    @classmethod
    def init(cls, left_port, right_port):
        left_motor = Motor(left_port)
        right_motor = Motor(right_port)
        return cls(left_motor, right_motor)

    def move_forward(self, speed):
        self.left.run(speed)
        self.right.run(speed)

    def stop(self):
        self.left.stop()
        self.right.stop()
