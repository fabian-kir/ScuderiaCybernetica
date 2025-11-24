import os
import sys

from pathlib import Path
env_emulator = os.environ.get("EV3_EMULATOR", "0") in ("1", "true", "True", "yes", "YES")
# Add the emulator pybricks shim to sys.path so `import pybricks` resolves to our emulator
this_file = Path(__file__).resolve()
software_root = this_file.parent.parent
emulator_root = software_root / "emulator_pybricks"

# Add both paths, with emulator taking priority
if str(emulator_root) not in sys.path:
    sys.path.insert(0, str(emulator_root))

from emulator_pybricks.runtime import launch_emulator
from software_ev3.controllers.controller import Controller
from software_ev3.hardware.robot_hub import RobotHub

# On the EV3 firmware this method exists, but add a fallback for host mode.
if not hasattr(RobotHub, "get_battery_voltage"):
    RobotHub.get_battery_voltage = RobotHub.get_battery_power

def main():
    """Entry-point that spins up the emulator UI and robot controller."""

    def run_robot():
        controller = Controller()
        controller.run()

    launch_emulator(run_robot)

if __name__ == "__main__":
    main()