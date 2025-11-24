import time

__all__ = ["StopWatch", "wait"]


class StopWatch:
    """Simplified StopWatch compatible with the Pybricks API."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._start = time.monotonic()
        self._paused = False
        self._pause_start = None
        self._pause_offset = 0.0

    def time(self) -> int:
        if self._paused and self._pause_start is not None:
            elapsed = self._pause_start - self._start - self._pause_offset
        else:
            elapsed = time.monotonic() - self._start - self._pause_offset
        return int(elapsed * 1000)

    def pause(self) -> None:
        if not self._paused:
            self._pause_start = time.monotonic()
            self._paused = True

    def resume(self) -> None:
        if self._paused and self._pause_start is not None:
            self._pause_offset += time.monotonic() - self._pause_start
            self._pause_start = None
            self._paused = False


def wait(duration_ms: int) -> None:
    """Blocking wait expressed in milliseconds to match Pybricks semantics."""
    time.sleep(duration_ms / 1000.0)

