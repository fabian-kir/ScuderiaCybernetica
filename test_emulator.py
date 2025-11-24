"""
Simple test script for the emulator

Tests basic functionality without running the full controller.
"""

import sys
from pathlib import Path

# Add emulator to path
emulator_root = Path(__file__).parent / "emulator_pybricks"
sys.path.insert(0, str(emulator_root))

# Start emulator UI
from emulator_pybricks.emulator_ui import emulator_ui
from emulator_pybricks.emulator_state import emulator_state
import threading
import time

# Start UI
emulator_ui.start()
time.sleep(1)  # Wait for UI to initialize

print("Testing emulator components...")

# Test imports
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor, TouchSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import StopWatch, wait

print("✓ All imports successful")

# Test hub
print("\nTesting EV3Brick...")
hub = EV3Brick()
hub.screen.print("Hello from emulator!")
hub.speaker.beep()
hub.light.on(Color.GREEN)
print("✓ Hub works")

# Test motor
print("\nTesting Motor...")
motor = Motor(Port.A)
motor.run(200)
time.sleep(0.5)
print(f"  Motor angle: {motor.angle():.1f}°")
print(f"  Motor speed: {motor.speed():.1f}°/s")
motor.hold()
print("✓ Motor works")

# Test color sensor
print("\nTesting ColorSensor...")
color_sensor = ColorSensor(Port.S1)
reflection = color_sensor.reflection()
print(f"  Reflection: {reflection}%")
print("✓ Color sensor works")

# Test ultrasonic sensor
print("\nTesting UltrasonicSensor...")
ultrasonic = UltrasonicSensor(Port.S4)
distance = ultrasonic.distance()
print(f"  Distance: {distance}mm")
print("✓ Ultrasonic sensor works")

# Test touch sensor
print("\nTesting TouchSensor...")
touch = TouchSensor(Port.S2)
pressed = touch.pressed()
print(f"  Pressed: {pressed}")
print("✓ Touch sensor works")

# Test stopwatch
print("\nTesting StopWatch...")
sw = StopWatch()
wait(100)
elapsed = sw.time()
print(f"  Elapsed time: {elapsed}ms")
print("✓ StopWatch works")

# Test button press
print("\nTesting button detection...")
hub.screen.print("Press CENTER button in UI...")
print("Press CENTER button in the emulator UI...")

# Wait for button press (with timeout)
timeout = time.time() + 10
while time.time() < timeout:
    from pybricks.ui import process_ui_events
    process_ui_events()
    
    buttons = hub.buttons.pressed()
    if buttons and Button.CENTER in buttons:
        print("✓ Button press detected!")
        hub.screen.print("Button press detected!")
        break
    
    time.sleep(0.05)
else:
    print("⚠ Button test timed out (no button pressed)")

print("\n" + "=" * 50)
print("All tests completed!")
print("=" * 50)
print("\nThe emulator UI should show:")
print("- 1 motor on Port A")
print("- 1 color sensor on Port S1")
print("- 1 ultrasonic sensor on Port S4")
print("- 1 touch sensor on Port S2")
print("- Console output with test messages")
print("\nClose the UI window to exit.")

# Keep running so UI stays open
try:
    while emulator_ui.running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nTest stopped by user")

