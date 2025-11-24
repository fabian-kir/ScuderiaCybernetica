from emulator_pybricks.runtime import get_runtime

__all__ = ["process_ui_events"]


def process_ui_events() -> None:
    """Yield control momentarily so the emulator UI can process events."""
    get_runtime().process_ui_events()

