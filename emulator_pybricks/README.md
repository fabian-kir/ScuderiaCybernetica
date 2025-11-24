# EV3 Pybricks Emulator

A complete software emulator for the Pybricks EV3 library, allowing you to test your EV3 robot code without physical hardware.

## Features

- **Full Motor Support**: Emulates all motor control modes (dc, run, run_time, run_angle, run_target, track_target)
- **Sensor Emulation**: Color, Ultrasonic, Touch, Gyro, and Infrared sensors
- **Interactive UI**: Real-time visualization and control of motors and sensors
- **Console Output**: View all print statements and system events
- **Button Simulation**: Simulate EV3 button presses (UP, DOWN, LEFT, RIGHT, CENTER)
- **Timing Simulation**: Realistic 50ms delays for sensor reads and motor.speed() calls
- **Physics Simulation**: Motors simulate realistic physics behavior

## Running the Emulator

Simply run the emulator_main.py script:

```bash
python emulator_main.py
```

The emulator will:
1. Start the physics simulation thread
2. Launch the UI window
3. Run your robot controller code

## UI Components

### Motors Panel
- Shows all registered motors with their ports
- Displays current mode (dc, run, hold, etc.)
- Shows angle and speed in real-time
- For DC mode: Allows manual speed input (simulates speed sensing in power mode)
- Shows control values (DC duty cycle, target speed, target angle)

### Sensors Panel
- **Color Sensor**: Adjustable slider for reflection value (0-100%)
- **Ultrasonic Sensor**: Input field for distance in millimeters
- **Touch Sensor**: Toggle button to simulate press/release

### EV3 Buttons
- Five buttons arranged like the physical EV3: UP, DOWN, LEFT, RIGHT, CENTER
- Click and hold to simulate button press
- Release to simulate button release

### Console Output
- Shows all screen.print() output
- Displays system events (sounds, LED changes, motor mode changes)
- Timestamped entries
- Auto-scrolls to latest output
- Clear button to reset console

### Hub Status
- Button LED color indicator
- Battery voltage display

## Motor Control Modes

The emulator supports all pybricks motor control modes:

- **dc()**: Direct duty cycle control (power mode)
- **run()**: Constant speed control
- **run_time()**: Run at speed for specific time
- **run_angle()**: Run at speed for specific angle
- **run_target()**: Run to absolute target angle
- **track_target()**: Smoothly track changing target angle
- **hold()**: Actively hold current position
- **stop()**: Stop and coast

## Special Features

### DC Mode Speed Control
When a motor runs in DC (power) mode, you can manually set the speed in the UI. This simulates the motor acting as a speed sensor, which is important for control algorithms that use `motor.speed()` while in power mode.

### Timing Simulation
- `sensor.reflection()`, `sensor.distance()`, `sensor.pressed()`: 50ms delay
- `motor.speed()`: 50ms delay
- All other operations: Instantaneous

### Physics Simulation
Motors simulate realistic physics:
- Speed gradually approaches target in RUN mode
- DC mode speed depends on duty cycle
- HOLD mode maintains zero speed
- Angle updates based on current speed

## Architecture

### Components

1. **emulator_state.py**: Central state management for all motors, sensors, and hub components
2. **emulator_ui.py**: Tkinter-based UI for visualization and control
3. **pybricks/**: Mock implementations of all pybricks modules
   - `hubs.py`: EV3Brick, Battery, Speaker, Screen, Buttons, Light
   - `ev3devices.py`: Motor, ColorSensor, UltrasonicSensor, TouchSensor, GyroSensor
   - `parameters.py`: Port, Button, Color, Stop, Direction
   - `tools.py`: StopWatch, wait, DataLog
   - `media/ev3dev.py`: SoundFile, ImageFile, Font
   - `robotics.py`: DriveBase
   - `ui.py`: process_ui_events (emulator-specific)

### Threading Model

- **Main Thread**: Runs the robot controller code
- **Physics Thread**: Updates motor physics at 60 FPS
- **UI Thread**: Handles Tkinter UI events and rendering

### State Management

All state is managed through the singleton `EmulatorState` class, which is thread-safe using locks. The UI and robot code communicate through this shared state.

## Differences from Real Hardware

1. **No Real Physics**: Motor physics are simulated with simple models
2. **Instantaneous Execution**: Most operations execute immediately (except sensor reads and motor.speed())
3. **Perfect Sensors**: Sensors return exact values with no noise
4. **No Hardware Limits**: No battery drain, motor wear, or physical constraints
5. **process_ui_events()**: This function is emulator-specific and doesn't exist in real pybricks

## Compatibility

The emulator implements pybricks v2.0 API and should be compatible with most EV3 MicroPython programs. Some advanced features may not be fully implemented.

## Known Limitations

- No graphical screen rendering (only text console)
- No sound playback (events logged to console)
- No file system emulation
- No Bluetooth/messaging support
- Simplified physics model

## Troubleshooting

### Import Errors
Make sure the emulator_pybricks directory is in your Python path before importing pybricks. The emulator_main.py script handles this automatically.

### UI Not Responding
If the UI becomes unresponsive, ensure you're calling `process_ui_events()` in any tight loops, especially in button wait loops.

### Timing Issues
If timing seems off, remember that the emulator runs faster than real-time in many cases. Sensor delays are simulated, but other operations are instantaneous.

## Credits

Created for the VmAtP (Vehicle mit automatischer Plattform) project by Scuderia Cybernetica.

