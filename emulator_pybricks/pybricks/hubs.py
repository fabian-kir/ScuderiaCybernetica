"""
Pybricks hubs module emulation

Provides the EV3Brick class.
"""

import time
from ..emulator_state import emulator_state
from .parameters import Button, Color


class Battery:
    """EV3 Battery"""
    
    def voltage(self) -> int:
        """
        Get battery voltage in millivolts
        
        Returns:
            Battery voltage in mV
        """
        return emulator_state.get_battery_voltage()
    
    def current(self) -> int:
        """Get battery current in milliamps"""
        return 500  # Arbitrary value for emulator


class Speaker:
    """EV3 Speaker"""
    
    def beep(self, frequency: int = 500, duration: int = 100):
        """
        Play a beep sound
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in milliseconds
        """
        emulator_state.beep(frequency, duration)
        # Don't actually wait in emulator
        # time.sleep(duration / 1000.0)
    
    def play_notes(self, notes, tempo=120):
        """Play musical notes"""
        emulator_state.log_event(f"🎵 Playing notes: {notes}")
    
    def play_file(self, file_name):
        """
        Play a sound file
        
        Args:
            file_name: Sound file constant from SoundFile
        """
        emulator_state.play_sound(str(file_name))
    
    def say(self, text):
        """Say text (text-to-speech)"""
        emulator_state.log_event(f"🗣️ Speaking: {text}")
    
    def set_speech_options(self, *args, **kwargs):
        """Set speech options"""
        pass
    
    def set_volume(self, volume, which="_all_"):
        """Set speaker volume"""
        emulator_state.log_event(f"🔊 Volume set to {volume}%")


class Light:
    """EV3 Button Light"""
    
    def on(self, color):
        """
        Turn on the button light with a specific color
        
        Args:
            color: Color constant from Color enum
        """
        emulator_state.set_button_led(color)
    
    def off(self):
        """Turn off the button light"""
        emulator_state.set_button_led(None)


class Screen:
    """EV3 Screen"""
    
    def __init__(self):
        self._font = None
    
    def set_font(self, font):
        """Set the font for text display"""
        self._font = font
    
    def clear(self):
        """Clear the screen"""
        emulator_state.screen_clear()
    
    def print(self, *args, sep=' ', end='\n'):
        """
        Print text to the screen
        
        Args:
            *args: Values to print
            sep: Separator between values
            end: End character
        """
        text = sep.join(str(arg) for arg in args)
        emulator_state.screen_print(text)
    
    def draw_text(self, x: int, y: int, text: str, text_color=Color.BLACK, background_color=None):
        """
        Draw text at a specific position
        
        Args:
            x: X coordinate
            y: Y coordinate
            text: Text to draw
            text_color: Text color
            background_color: Background color
        """
        emulator_state.screen_print(f"[{x},{y}] {text}")
    
    def draw_box(self, x: int, y: int, width: int, height: int, r: int = 0, fill: bool = False):
        """Draw a box"""
        pass
    
    def draw_circle(self, x: int, y: int, radius: int, fill: bool = False):
        """Draw a circle"""
        pass
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 1):
        """Draw a line"""
        pass
    
    def draw_pixel(self, x: int, y: int, color=Color.BLACK):
        """Draw a single pixel"""
        pass
    
    def load_image(self, filename):
        """Load an image"""
        pass
    
    def draw_image(self, x: int, y: int, source, transparent=None):
        """Draw an image"""
        pass


class Buttons:
    """EV3 Buttons"""
    
    def pressed(self):
        """
        Check which buttons are currently pressed
        
        Returns:
            List of Button constants, or empty list if no buttons pressed
        """
        pressed = emulator_state.get_pressed_buttons()
        
        if not pressed:
            return []
        
        # Convert string names to Button enum
        button_list = []
        for btn_name in pressed:
            try:
                button_list.append(Button[btn_name])
            except KeyError:
                pass
        
        return button_list if button_list else []


class EV3Brick:
    """
    EV3 Brick (Hub)
    
    Main hub controlling the robot. Provides access to:
    - Battery
    - Buttons
    - Speaker
    - Light (button LED)
    - Screen
    """
    
    def __init__(self):
        """Initialize the EV3 Brick"""
        self.battery = Battery()
        self.buttons = Buttons()
        self.speaker = Speaker()
        self.light = Light()
        self.screen = Screen()
        
        emulator_state.log_event("EV3Brick initialized")

