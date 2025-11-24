from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.media.ev3dev import SoundFile
from pybricks.media.ev3dev import Font
import time

from software_ev3.utils.singleton import singleton

# Import UI event processor for emulator mode
try:
    from pybricks.ui import process_ui_events
except ImportError:
    process_ui_events = None


@singleton
class RobotHub:
    def __init__(self, enable_startup_feedback = True):
        print("Setting up the EV3 Hub")
        self.hub = EV3Brick()

        self.hub.screen.set_font(Font(size=6))
        
        if enable_startup_feedback:
            self.hub.speaker.beep()
            self.hub.screen.print("Initializing hardware...")

    def get_battery_power(self):
        return self.hub.battery.voltage() / 1000.0 # output in V instead of mV

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
            # Process UI events to allow button presses to register (for emulator)
            if process_ui_events:
                try:
                    process_ui_events()
                except Exception:
                    pass
            
            pressed = self.hub.buttons.pressed()
            if pressed is not None and Button.CENTER in pressed:
                break
            
            # Small sleep to prevent excessive CPU usage and allow UI to update
            time.sleep(0.01)  # 10ms sleep

        # wait for CENTER button to be released again
        while True:
            # Process UI events to allow button releases to register (for emulator)
            if process_ui_events:
                try:
                    process_ui_events()
                except Exception:
                    pass
            
            pressed = self.hub.buttons.pressed()
            if pressed is None or Button.CENTER not in pressed:
                break
            
            # Small sleep to prevent excessive CPU usage and allow UI to update
            time.sleep(0.01)  # 10ms sleep

        if play_button_respond_sound:
            self.hub.speaker.play_file(SoundFile.CLICK)

        return

    def update(self, dt):
        """Periodic update logic."""
        pass