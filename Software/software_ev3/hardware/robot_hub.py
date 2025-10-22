from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.media.ev3dev import SoundFile

from Software.software_ev3.hardware.hardware_wrapper import HardwareWrapper


class RobotHub(HardwareWrapper):
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

    def await_user_confirmation(self, play_button_respond_sound = True):
        """Wait for user to press and release middle button."""

        # wait for middle button to be pressed
        while True:
            if Button.MIDDLE in self.hub.buttons.pressed():
                break

        # wait for middle button to be released again
        while True:
            if Button.MIDDLE not in self.hub.buttons.pressed():
                break

        if play_button_respond_sound:
            self.hub.speaker.play_file(SoundFile.CLICK)

        return