from pybricks.hubs import EV3Brick

class RobotHub:
    _instance = None
    def __new__(cls):
        if cls._instance is not None:
            return cls._instance
        
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self, enable_startup_feedback = True):
        print("Setting up the EV3 Hub")
        self.hub = EV3Brick()
        
        if enable_startup_feedback:
            self.hub.speaker.beep()
            self.hub.screen.print("Initializing hardware...")

    def display(self, text):
        """Display text on the EV3 screen."""
        self.hub.screen.clear()
        self.hub.screen.print(text)

    def beep(self):
        """Make a simple beep."""
        self.hub.speaker.beep()

    def set_led(self, color):
        """Change LED color."""
        self.hub.light.on(color)
