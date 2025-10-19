from hardware import BalanceMotor, DistanceSensor, PowerTrain, RobotHub, SlopeSensor
from pybricks.tools import wait


class Controller:
    """Main controller coordinating robot behavior."""

    _instance = None
    @classmethod
    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self, hardware):
        self.hub = RobotHub()
        self.power_train = PowerTrain()
        self.balance_motor = BalanceMotor()
        self.slope_sensor = SlopeSensor()
        self.distance_sensor = DistanceSensor()

        # TODO: Add more system states (running, mode, etc.)
        # TODO make this an enum that switches state, not a bool for every state!
        self.running = False

    def run(self):
        """Main control loop."""
        self.running = True
        # TODO: Add startup checks or calibration
        try:
            while self.running:
                self.update()
                #wait(100) # why wait? we gotta run at full speed! -> Better: use timing modules
        except KeyboardInterrupt:
            self.stop()

    def update(self):
        """Periodic update logic."""
        # TODO: Read sensors, decide actions, control motors
        pass

    def stop(self):
        """Stop all motors safely."""
        self.running = False
        # TODO: Add graceful stop behavior
