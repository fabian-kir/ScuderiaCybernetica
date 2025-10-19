from pybricks.tools import wait


class Controller:
    """Main controller coordinating robot behavior."""

    @classmethod
    def init(cls, hardware):
        """Factory method to initialize controller."""
        return cls(hardware)

    def __init__(self, hardware):
        """Map hardware components."""
        self.hub = hardware["robot_hub"]
        self.power_train = hardware["power_train"]
        self.balance_motor = hardware["balance_motor"]
        self.slope_sensor = hardware["slope_sensor"]
        self.distance_sensor = hardware["distance_sensor"]

        # TODO: Add more system states (running, mode, etc.)
        self.running = False

    def run(self):
        """Main control loop."""
        self.running = True
        # TODO: Add startup checks or calibration
        try:
            while self.running:
                self.update()
                wait(100)
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
