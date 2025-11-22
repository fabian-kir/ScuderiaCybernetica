import time
import os

def wait(ms: int) -> None:
	"""Block for the given milliseconds."""
	# In emulator mode, periodically process UI events to keep window responsive
	if os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES"):
		from .ui import process_ui_events
		# Process events in small chunks to keep UI responsive
		elapsed = 0
		chunk_ms = 10  # Process events every 10ms
		while elapsed < ms:
			time.sleep(min(chunk_ms / 1000.0, (ms - elapsed) / 1000.0))
			elapsed += chunk_ms
			try:
				process_ui_events()
			except Exception:
				# Window closed or error, fall back to normal sleep
				time.sleep((ms - elapsed) / 1000.0)
				break
	else:
		time.sleep(ms / 1000.0)


class StopWatch:
	def __init__(self) -> None:
		self._start = time.perf_counter()

	def time(self) -> int:
		"""Elapsed time in milliseconds."""
		return int((time.perf_counter() - self._start) * 1000)


