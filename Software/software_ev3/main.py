#!/usr/bin/env pybricks-micropython
import os
import sys
from pathlib import Path

from Software.emulator_pybricks.pybricks.parameters import Port

# Enable emulator mode if requested before importing anything that uses pybricks
if os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES"):
	# Add the emulator pybricks shim to sys.path so `import pybricks` resolves to our emulator
	this_file = Path(__file__).resolve()
	software_root = this_file.parent.parent
	emulator_root = software_root / "emulator_pybricks"
	
	# Add both paths, with emulator taking priority
	if str(emulator_root) not in sys.path:
		sys.path.insert(0, str(emulator_root))
	if str(software_root) not in sys.path:
		sys.path.insert(0, str(software_root))

from controllers.controller import Controller

def main():
	# Create controller and start behavior
	controller = Controller()
	controller.run()

if __name__ == "__main__":
    main()