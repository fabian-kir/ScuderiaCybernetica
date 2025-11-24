from __future__ import annotations

from typing import Tuple

from emulator_pybricks.runtime import EmulatorRuntime, get_runtime

__all__ = ["EV3Brick"]


class EV3Brick:
    """Very small EV3 hub façade backed by the emulator runtime."""

    def __init__(self):
        self._runtime = get_runtime()
        self.screen = _Screen(self._runtime)
        self.speaker = _Speaker(self._runtime)
        self.buttons = _Buttons(self._runtime)
        self.light = _Light(self._runtime)
        self.battery = _Battery(self._runtime)


class _Screen:
    def __init__(self, runtime: EmulatorRuntime):
        self._runtime = runtime
        self._font = None

    def set_font(self, font) -> None:
        self._font = font
        self._runtime.append_console(f"Screen font set to {font}", level="debug")

    def clear(self) -> None:
        self._runtime.append_console("Screen cleared", level="debug")

    def print(self, *args) -> None:
        text = " ".join(str(arg) for arg in args)
        self._runtime.append_console(f"SCREEN: {text}")

    def draw_text(self, x: int, y: int, text: str) -> None:
        self._runtime.append_console(f"Screen draw at ({x}, {y}): {text}")


class _Speaker:
    def __init__(self, runtime: EmulatorRuntime):
        self._runtime = runtime

    def beep(self) -> None:
        self._runtime.append_console("Speaker beep")

    def play_file(self, sound_file) -> None:
        self._runtime.append_console(f"Speaker play: {sound_file}")


class _Buttons:
    def __init__(self, runtime: EmulatorRuntime):
        self._runtime = runtime

    def pressed(self) -> Tuple:
        return self._runtime.get_pressed_buttons()


class _Light:
    def __init__(self, runtime: EmulatorRuntime):
        self._runtime = runtime
        self._color = None

    def on(self, color) -> None:
        self._color = color
        self._runtime.append_console(f"LED color set to {color}")

    def off(self) -> None:
        self._color = None
        self._runtime.append_console("LED turned off")


class _Battery:
    def __init__(self, runtime: EmulatorRuntime):
        self._runtime = runtime

    def voltage(self) -> int:
        """Return current voltage in mV to match Pybricks."""
        return self._runtime.get_battery_voltage_mv()

