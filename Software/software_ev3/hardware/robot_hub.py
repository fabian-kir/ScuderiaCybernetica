from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.media.ev3dev import SoundFile

from utils.singleton import singleton


@singleton
class RobotHub:
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

    def print(self, *args):
        self.hub.screen.print(*args)
        print(*args)

    def beep(self):
        """Make a simple beep."""
        self.hub.speaker.beep()

    def play_startup_sound(self):
        self.hub.speaker.play_file(SoundFile.SPEED_UP)

    def set_led(self, color):
        """Change LED color."""
        self.hub.light.on(color)

    def await_user_confirmation(self, message="", play_user_prompt_sound=True, play_button_respond_sound=True):
        """Wait for user to press and release CENTER button."""

        if message:
            self.hub.screen.clear()
            self.hub.screen.draw_text(20, 20, message)

        if play_user_prompt_sound:
            self.hub.speaker.play_file(SoundFile.CONFIRM)

        # wait for CENTER button to be pressed
        while True:
            if Button.CENTER in self.hub.buttons.pressed():
                break

        # wait for CENTER button to be released again
        while True:
            if Button.CENTER not in self.hub.buttons.pressed():
                break

        if play_button_respond_sound:
            self.hub.speaker.play_file(SoundFile.CLICK)

        return

    def update(self, dt):
        """Periodic update logic."""
        pass