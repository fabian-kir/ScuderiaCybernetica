class SoundFile:
    """Subset of the EV3 sound file constants."""

    CLICK = "click"
    CONFIRM = "confirm"
    ERROR = "error"
    ALERT = "alert"


class Font:
    """Minimal font placeholder used by the EV3 screen emulator."""

    def __init__(self, family: str = "Lucida Console", size: int = 12):
        self.family = family
        self.size = size

    def __repr__(self) -> str:  # pragma: no cover - helper for debugging
        return f"Font(family={self.family!r}, size={self.size})"


__all__ = ["SoundFile", "Font"]

