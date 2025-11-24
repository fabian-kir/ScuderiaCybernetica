"""
Pybricks UI module for emulator

Provides process_ui_events function for UI integration.
"""

from ..emulator_ui import emulator_ui


def process_ui_events():
    """
    Process UI events (emulator-specific)
    
    This function should be called periodically to allow the emulator UI
    to process events and update. It's used in loops where button presses
    need to be detected.
    
    In the real pybricks, this function doesn't exist. It's specific to
    the emulator to allow the UI thread to update.
    """
    # Check if UI is running
    if emulator_ui.running and emulator_ui.root:
        try:
            # Process pending events
            emulator_ui.root.update()
        except Exception:
            # UI might have been closed
            pass

