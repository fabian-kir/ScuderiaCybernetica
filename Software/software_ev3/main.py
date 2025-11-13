#!/usr/bin/env pybricks-micropython
import os
import sys

pathlib_exists = True
try:
	from pathlib import Path
except ImportError:
	pathlib_exists = False

# Auto-enable emulator on non-EV3 platforms (macOS, Windows, Linux)
# EV3 runs MicroPython which doesn't have pathlib, so if pathlib exists, we're likely on a regular OS
# Also check if EV3_EMULATOR is explicitly set
env_emulator = os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES")
# Auto-detect: if pathlib exists (not MicroPython) and not on actual EV3 hardware
is_ev3_hardware = sys.platform == "linux" and os.path.exists("/sys/class/lego-port")
should_use_emulator = env_emulator or (pathlib_exists and not is_ev3_hardware)

# Enable emulator mode if requested before importing anything that uses pybricks
if should_use_emulator and pathlib_exists:
	# Add the emulator pybricks shim to sys.path so `import pybricks` resolves to our emulator
	this_file = Path(__file__).resolve()
	software_root = this_file.parent.parent
	emulator_root = software_root / "emulator_pybricks"
	
	# Add both paths, with emulator taking priority
	if str(emulator_root) not in sys.path:
		sys.path.insert(0, str(emulator_root))
	print(f"EV3 Emulator enabled (EV3_EMULATOR={os.environ.get('EV3_EMULATOR', 'auto')})")

import pybricks.robotics

from controllers.controller import Controller

def main():
	# Create controller and start behavior
	controller = Controller()
	controller.run()

if __name__ == "__main__":
    main()