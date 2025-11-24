import os
import sys
import threading
import time

from pathlib import Path

# Add the emulator pybricks shim to sys.path so `import pybricks` resolves to our emulator
this_file = Path(__file__).resolve()
emulator_root = this_file.parent / "emulator_pybricks"

# Add emulator path, with emulator taking priority
if str(emulator_root) not in sys.path:
    sys.path.insert(0, str(emulator_root))

# Import emulator components
from emulator_pybricks.emulator_state import emulator_state
from emulator_pybricks.emulator_ui import emulator_ui

from software_ev3.controllers.controller import Controller


def physics_simulation_thread():
    """
    Background thread to simulate motor physics.
    
    Updates motor angles and speeds based on their control modes.
    """
    print("Starting physics simulation thread...")
    last_time = time.time()
    
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Simulate motor physics
        emulator_state.simulate_motor_physics(dt)
        
        # Run at ~60 FPS
        time.sleep(1.0 / 60.0)


def main():
    """
    Main entry point for the emulator.
    
    Starts the UI, physics simulation, and controller.
    """
    print("=" * 60)
    print("EV3 Pybricks Emulator")
    print("=" * 60)
    print()
    print("Starting emulator components...")
    print()
    
    # Start physics simulation thread
    physics_thread = threading.Thread(target=physics_simulation_thread, daemon=True)
    physics_thread.start()
    print("✓ Physics simulation started")
    
    # Start UI in background thread
    emulator_ui.start()
    print("✓ UI starting...")
    
    # Wait a bit for UI to initialize
    time.sleep(0.5)
    
    # Start controller in main thread
    print("✓ Starting robot controller")
    print()
    print("=" * 60)
    print()
    
    try:
        controller = Controller()
        controller.run()
    except KeyboardInterrupt:
        print("\n\nEmulator stopped by user")
    except Exception as e:
        print(f"\n\nError in controller: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nShutting down emulator...")
        emulator_ui.stop()


if __name__ == "__main__":
    main()