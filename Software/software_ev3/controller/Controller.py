from hardware import BalanceMotor, DistanceSensor, PowerTrain, RobotHub, SlopeSensor
from pybricks.tools import wait, StopWatch


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
    """Main control loop with delta timing using Pybricks StopWatch."""

    self.running = True
    sw = StopWatch()          # starts at 0 ms
    last_ms = sw.time()       # initial timestamp

    try:
        while self.running:
            now_ms = sw.time()
            dt = (now_ms - last_ms) / 1000.0  # convert to seconds
            last_ms = now_ms

            # expose dt for update(); keep signature of update() unchanged
            self.time_delta = dt

            self.update()
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
