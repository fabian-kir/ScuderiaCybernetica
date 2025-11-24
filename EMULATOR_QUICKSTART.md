# EV3 Pybricks Emulator - Quick Start Guide

## Overview

This emulator allows you to test your EV3 robot code without the physical hardware. It provides a graphical UI to monitor motors and sensors in real-time.

## Running Your Robot Code

### Option 1: Run the Full Controller (Recommended)

```bash
python emulator_main.py
```

This will:
1. Start the emulator UI
2. Initialize all hardware components
3. Run your robot controller

### Option 2: Run the Test Script

```bash
python test_emulator.py
```

This runs a simple test to verify the emulator works correctly.

## Using the Emulator UI

### Motors Panel
Shows all motors connected to your robot:
- **Port**: Which port the motor is connected to (A, B, C, D)
- **Mode**: Current control mode (dc, run, hold, etc.)
- **Angle**: Current rotation angle in degrees
- **Speed**: Current speed in degrees per second
- **Control Value**: The target/control value (DC duty cycle, target speed, etc.)

**Special Feature for DC Mode:**
When a motor runs in DC (power) mode, you can manually set its speed using the input field. This simulates the motor's speed sensor, which is critical for control algorithms that use `motor.speed()` while in power mode.

### Sensors Panel
Shows all sensors and allows you to control their values:

- **Color Sensor**: Use the slider to set reflection value (0-100%)
- **Ultrasonic Sensor**: Enter distance in millimeters
- **Touch Sensor**: Click "Toggle Press" to simulate pressing/releasing

### EV3 Buttons
Five buttons arranged like the physical EV3:
```
      UP
LEFT CENTER RIGHT
     DOWN
```
Click and hold to press, release to simulate button release.

### Console Output
- Shows all `screen.print()` output
- Displays system events (sounds, LED changes, motor mode changes)
- Timestamps for all entries
- Auto-scrolls to latest output
- Clear button to reset

### Hub Status
- **Button LED**: Shows current LED color
- **Battery**: Displays battery voltage (default 8.0V)

## Key Features

### Realistic Timing
- Sensor reads (`reflection()`, `distance()`, `pressed()`): 50ms delay
- Motor speed reads (`motor.speed()`): 50ms delay
- All other operations: Instantaneous

### Physics Simulation
Motors simulate realistic behavior:
- Speed gradually approaches target in RUN mode
- DC mode speed depends on duty cycle
- HOLD mode maintains zero speed
- Angle updates based on current speed

### Thread Safety
The emulator uses multiple threads:
- **Main Thread**: Runs your controller code
- **Physics Thread**: Simulates motor physics (60 FPS)
- **UI Thread**: Handles user interface

All threads safely share state through thread-safe locks.

## Troubleshooting

### UI Not Responding
If loops are blocking the UI, add `process_ui_events()` calls:

```python
from pybricks.ui import process_ui_events

while condition:
    process_ui_events()  # Allow UI to update
    # your code here
```

### Import Errors
The emulator should work automatically with `emulator_main.py`. If you get import errors, ensure the `emulator_pybricks` directory is in your Python path.

### Motor Not Moving
1. Check the UI to verify the motor is registered
2. Verify the control mode is correct
3. Check if the target speed/angle is set
4. Look at the console for any error messages

### Sensor Values Not Changing
1. Verify the sensor is registered in the Sensors panel
2. Adjust the sensor value in the UI
3. Note that sensor reads have a 50ms delay (this is realistic)

## Your Robot Configuration

Based on your code, your robot has:

**Motors:**
- Port A: Drive Motor (with PID speed control)
- Port B: Large Balance Motor (platform forward/X axis)
- Port C: Small Balance Motor (platform sideways/Y axis)

**Sensors:**
- Port S1: Color Sensor (for line tracking)
- Port S2: Left Touch Sensor
- Port S3: Right Touch Sensor
- Port S4: Ultrasonic Sensor (for distance measurement)

## Tips for Testing

1. **Start Simple**: Test individual components before running the full controller
2. **Watch the Console**: Look for initialization messages and errors
3. **Adjust Sensor Values**: Change sensor values while running to test different scenarios
4. **Monitor Motor Modes**: Watch how motors switch between modes during operation
5. **Test Button Handling**: Use the UI buttons to test your button handling code

## Limitations

- No graphical screen rendering (text console only)
- No actual sound playback (events logged to console)
- Simplified physics model
- No Bluetooth/messaging support
- Sensor values don't have realistic noise

## Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your configuration in `software_ev3/config/constants.py`
3. Review the emulator README at `emulator_pybricks/README.md`

## Example: Manual Sensor Control

While your robot is running, you can:

1. **Simulate Line Following**: Adjust the color sensor reflection slider to see how the platform responds
2. **Test Distance Control**: Change the ultrasonic distance to simulate obstacles
3. **Trigger Emergency Stop**: Toggle the touch sensor to test your safety features
4. **Test Button Menus**: Use the EV3 buttons to navigate through any menus

Enjoy testing your robot! 🤖

