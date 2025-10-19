from pybricks.ev3devices import Motor

class BalanceMotor:
    def __init__(self, motor):
        self.motor = motor

    @classmethod
    def init(cls, port):
        motor = Motor(port)
        return cls(motor)

    def balance(self, speed):
        """Run the balance motor to keep robot stable."""
        self.motor.run(speed)

    def stop(self):
        """Stop balancing."""
        self.motor.stop()
