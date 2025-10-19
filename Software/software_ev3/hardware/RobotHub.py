from pybricks.hubs import EV3Brick

class RobotHub:
    def __init__(self, hub):
        self.hub = hub

    @classmethod
    def init(cls):
        hub = EV3Brick()
        # optional startup feedback
        hub.speaker.beep()
        hub.screen.print("Initializing hardware...")
        return cls(hub)

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
