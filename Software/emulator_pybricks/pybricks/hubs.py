from .state import EMU_STATE
from .ui import ensure_ui_started, process_ui_events
from .parameters import Button


class _Screen:
	def clear(self):
		# No persistent buffer in emulator
		return

	def print(self, *args):
		# Print to host console
		print("[EV3 SCREEN]", *args)

	def draw_text(self, x, y, text):
		print(f"[EV3 SCREEN] draw text at {x}, {y}: {text}")


class _Speaker:
	def beep(self):
		print("[EV3 SPEAKER] beep")

	def play_file(self, soundfile):
		print(f"[EV3 SPEAKER] play {soundfile}")


class _Light:
	def on(self, color):
		print(f"[EV3 LIGHT] {color}")


class _Buttons:
	def pressed(self):
		process_ui_events()
		pressed_buttons = []
		for button_name in EMU_STATE.get_pressed_buttons():
			# Map button names to Button enum values
			if button_name == "LEFT":
				pressed_buttons.append(Button.LEFT)
			elif button_name == "RIGHT":
				pressed_buttons.append(Button.RIGHT)
			elif button_name == "UP":
				pressed_buttons.append(Button.UP)
			elif button_name == "DOWN":
				pressed_buttons.append(Button.DOWN)
			elif button_name == "MIDDLE":
				pressed_buttons.append(Button.MIDDLE)
		return pressed_buttons


class EV3Brick:
	def __init__(self):
		ensure_ui_started()
		self.screen = _Screen()
		self.speaker = _Speaker()
		self.light = _Light()
		self.buttons = _Buttons()


