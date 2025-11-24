# Pybricks Emulator

This folder contains a lightweight desktop emulator for the EV3 Pybricks
runtime so the project can be executed without the physical brick.

## Running the emulator

1. Install the project dependencies as usual (no additional packages are
   required; the emulator only depends on Tk, which ships with Python on macOS).
2. Launch the emulator entry-point:

   ```bash
   python3 emulator_main.py
   ```

   This starts the Tk UI and spawns the regular `Controller` inside a worker
   thread. All other modules stay untouched, so the same code keeps running on
   the EV3 via `onboard_main.py`.

## UI overview

The window is intentionally simple and focuses on the debugging features that
were requested:

- **Motors panel** – lists every instantiated motor together with its port,
  current mode (`run`, `dc`, `hold`, …), command value and measured angle. When
  a motor operates in power (`dc`) mode you can use the “Simulated speed” slider
  to define the measured speed that `motor.speed()` should report. This makes
  it possible to test the drive PID loop locally.
- **Sensors panel** – shows all registered sensors. Selecting one exposes either
  a slider (color reflection, ultrasonic distance) or a toggle (touch sensors)
  so you can decide what value `sensor.reflection()` / `sensor.distance()` /
  `sensor.pressed()` returns.
- **Inputs & status panel** – provides clickable EV3 buttons (center/up/down/
  left/right), live battery voltage control, and the current controller thread
  status. Button presses immediately propagate to `RobotHub().await_user_confirmation`.
- **Console panel** – streams everything printed to the EV3 screen, hub LED
  changes, speaker events, and other emulator messages. Use the clear button to
  shorten long sessions.

All sensor reads and `motor.speed()` calls incur a 50 ms delay to match the
behaviour observed on the real brick.

## Limitations

- Only the subset of Pybricks APIs required by `software_ev3` is implemented.
- The motor model is kinematic rather than physical; it integrates command
  speeds over time but does not simulate inertia.
- Closing the emulator window stops the UI loop; the robot thread is marked as
  daemon and will terminate alongside the process.

