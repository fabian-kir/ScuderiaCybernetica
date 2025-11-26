import os
import sys

from pathlib import Path

env_emulator = os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES")
# Ensure imports resolve relative to the project root (this file's directory)
# and load the emulator shim for `pybricks` before anything attempts to import it.
this_file = Path(__file__).resolve()
project_root = this_file.parent
emulator_root = project_root / "emulator_pybricks"

# Add both paths, with emulator taking priority
if str(emulator_root) not in sys.path:
    sys.path.insert(0, str(emulator_root))

from software_ev3.hardware.drive_motor import DriveMotor
from emulator_pybricks.runtime import launch_emulator
from software_ev3.controllers.controller import Controller

from time import sleep

def main():
    """Entry-point that spins up the emulator UI and robot controller."""

    def run_robot():
        controller = Controller()
        controller.run()

    launch_emulator(run_robot)
    sleep(10_000_000)

if __name__ == "__main__":
    main()