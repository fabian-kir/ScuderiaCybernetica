from config.ports import PORTS
from pybricks.ev3devices import Motor


class BalanceMotor:
    _instance = None
    def __new__(cls):
        # Making sure only ever one instance exists
        if cls._instance is not None:
            return cls._instance
        
        # Creating a new instance
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self):
        self.port = PORTS["BALANCE_MOTOR"]
        print("Setting up balance motor on port:", self.port)
        self.motor = Motor(self.port)


    def balance(self, speed):
        """Run the balance motor to keep robot stable."""
        self.motor.run(speed)

    def stop(self):
        """Stop balancing."""
        self.motor.stop()
