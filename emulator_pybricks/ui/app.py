from __future__ import annotations

import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from emulator_pybricks.runtime import EmulatorRuntime, get_runtime
from pybricks.parameters import Button

__all__ = ["EmulatorApp"]


class EmulatorApp:
    """Web-based UI for inspecting and manipulating the emulated EV3 state."""

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8765
    PORT_RETRIES = 20

    def __init__(
        self,
        runtime: Optional[EmulatorRuntime] = None,
        *,
        host: str = DEFAULT_HOST,
        port: Optional[int] = None,
        auto_open_browser: bool = True,
    ) -> None:
        self.runtime = runtime or get_runtime()
        self.host = host
        self.port = port or self.DEFAULT_PORT
        self.auto_open_browser = auto_open_browser

        self._server: Optional[ThreadingHTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._base_url: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self._start_server()
        if self.auto_open_browser:
            self._open_browser()
        print(f"[Emulator] UI available at {self._base_url}")
        try:
            while not self.runtime.should_shutdown():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.runtime.request_shutdown()
        finally:
            self._stop_server()

    # ------------------------------------------------------------------ #
    # Server lifecycle
    # ------------------------------------------------------------------ #
    def _start_server(self) -> None:
        handler_cls = self._make_handler_class()
        last_error: Optional[Exception] = None
        port = self.port
        for _ in range(self.PORT_RETRIES + 1):
            try:
                server = ThreadingHTTPServer((self.host, port), handler_cls)
                server.daemon_threads = True
                self._server = server
                self.port = port
                self._base_url = f"http://{self.host}:{self.port}"
                break
            except OSError as exc:
                last_error = exc
                port += 1
        if self._server is None:
            raise RuntimeError("Unable to launch emulator UI server") from last_error
        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            kwargs={"poll_interval": 0.1},
            name="EmulatorUIServer",
            daemon=True,
        )
        self._server_thread.start()

    def _stop_server(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            finally:
                self._server = None
        if self._server_thread:
            self._server_thread.join(timeout=1.0)
            self._server_thread = None

    def _open_browser(self) -> None:
        if not self._base_url:
            return
        try:
            webbrowser.open(self._base_url, new=1, autoraise=True)
        except Exception:
            print(f"[Emulator] Please open {self._base_url} manually.")

    # ------------------------------------------------------------------ #
    # HTTP handling
    # ------------------------------------------------------------------ #
    def _make_handler_class(self):  # type: ignore[override]
        runtime = self.runtime

        class EmulatorRequestHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover
                return

            # ------------------------------- GET endpoints ------------------------------- #
            def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path in ("/", "/index.html"):
                    self._serve_bytes(INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
                    return
                if parsed.path == "/app.css":
                    self._serve_bytes(APP_CSS.encode("utf-8"), "text/css; charset=utf-8")
                    return
                if parsed.path == "/app.js":
                    self._serve_bytes(APP_JS.encode("utf-8"), "application/javascript; charset=utf-8")
                    return
                if parsed.path == "/state":
                    self._handle_state(parsed)
                    return
                self.send_error(404, "Not found")

            # ------------------------------ POST endpoints ------------------------------- #
            def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path == "/shutdown":
                    runtime.request_shutdown()
                    self._serve_json({"ok": True})
                    return

                segments = [segment for segment in parsed.path.split("/") if segment]
                try:
                    if len(segments) == 3 and segments[0] == "motors" and segments[2] == "feedback":
                        self._handle_motor_feedback(segments[1])
                        return
                    if len(segments) == 2 and segments[0] == "sensors":
                        self._handle_sensor_update(segments[1])
                        return
                    if len(segments) == 2 and segments[0] == "buttons":
                        self._handle_button_update(segments[1])
                        return
                    if parsed.path == "/battery":
                        self._handle_battery_update()
                        return
                except ValueError as exc:
                    self._serve_json({"error": str(exc)}, status=400)
                    return

                self.send_error(404, "Not found")

            # ------------------------------ Handlers ------------------------------------- #
            def _handle_state(self, parsed) -> None:
                params = parse_qs(parsed.query or "")
                try:
                    last_seq = int(params.get("last_seq", ["0"])[0])
                except ValueError:
                    last_seq = 0
                events, new_seq = runtime.consume_console_events(last_seq)
                payload = {
                    "motors": runtime.snapshot_motors(),
                    "sensors": runtime.snapshot_sensors(),
                    "buttons": [getattr(btn, "name", str(btn)) for btn in runtime.get_pressed_buttons()],
                    "battery_voltage": runtime.get_battery_voltage_mv() / 1000.0,
                    "robot_running": runtime.is_robot_running(),
                    "console_events": events,
                    "console_seq": new_seq,
                    "shutdown": runtime.should_shutdown(),
                }
                self._serve_json(payload)

            def _handle_motor_feedback(self, motor_id: str) -> None:
                payload = self._json_body()
                if "speed" not in payload:
                    raise ValueError("Missing speed value")
                speed = float(payload["speed"])
                runtime.set_motor_feedback(motor_id, speed)
                self._serve_json({"ok": True})

            def _handle_sensor_update(self, sensor_id: str) -> None:
                payload = self._json_body()
                if "value" not in payload:
                    raise ValueError("Missing sensor value")
                runtime.set_sensor_value(sensor_id, payload["value"])
                self._serve_json({"ok": True})

            def _handle_button_update(self, button_name: str) -> None:
                payload = self._json_body()
                name = button_name.upper()
                try:
                    button = Button[name]
                except KeyError as exc:
                    raise ValueError(f"Unknown button '{button_name}'") from exc
                pressed = bool(payload.get("pressed"))
                runtime.set_button_state(button, pressed)
                self._serve_json({"ok": True})

            def _handle_battery_update(self) -> None:
                payload = self._json_body()
                if "voltage" not in payload:
                    raise ValueError("Missing voltage value")
                voltage_v = float(payload["voltage"])
                runtime.set_battery_voltage_mv(int(voltage_v * 1000))
                self._serve_json({"ok": True})

            # ------------------------------ Helpers -------------------------------------- #
            def _json_body(self) -> Dict[str, Any]:
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b""
                if not raw:
                    return {}
                return json.loads(raw.decode("utf-8"))

            def _serve_json(self, payload: Dict[str, Any], status: int = 200) -> None:
                body = json.dumps(payload).encode("utf-8")
                self._serve_bytes(body, "application/json; charset=utf-8", status=status)

            def _serve_bytes(self, payload: bytes, content_type: str, status: int = 200) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(payload)

        return EmulatorRequestHandler


INDEX_HTML = """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Pybricks EV3 Emulator</title>
    <link rel=\"stylesheet\" href=\"/app.css\" />
  </head>
  <body>
    <header class=\"app-header\">
      <div>
        <h1>Pybricks EV3 Emulator</h1>
        <p>Use sliders and buttons to emulate motors, sensors, and hub inputs.</p>
      </div>
      <div class=\"status-block\">
        <span id=\"status-text\">Connecting…</span>
      </div>
    </header>
    <main class=\"app-grid\">
      <section class=\"panel\" id=\"motors-panel\">
        <div class=\"panel-header\">
          <h2>Motors</h2>
        </div>
        <div class=\"table-wrapper\">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Port</th>
                <th>Mode</th>
                <th>Command</th>
                <th>Speed</th>
                <th>Angle</th>
              </tr>
            </thead>
            <tbody id=\"motors-body\"></tbody>
          </table>
        </div>
        <div class=\"panel-footer\">
          <div class=\"control-line\">
            <span class=\"label\">Selected:</span>
            <span id=\"motor-details\">None</span>
          </div>
          <label class=\"control-line\">
            Simulated speed (deg/s)
            <input type=\"range\" id=\"motor-speed\" min=\"-1000\" max=\"1000\" step=\"5\" value=\"0\" disabled />
            <span id=\"motor-speed-value\">0</span>
          </label>
        </div>
      </section>

      <section class=\"panel\" id=\"sensors-panel\">
        <div class=\"panel-header\">
          <h2>Sensors</h2>
        </div>
        <div class=\"table-wrapper\">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Port</th>
                <th>Type</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody id=\"sensors-body\"></tbody>
          </table>
        </div>
        <div class=\"panel-footer\">
          <div class=\"control-line\">
            <span class=\"label\">Selected:</span>
            <span id=\"sensor-details\">None</span>
          </div>
          <div class=\"sensor-controls\">
            <label id=\"sensor-slider-wrapper\">
              Value
              <input type=\"range\" id=\"sensor-value\" min=\"0\" max=\"100\" step=\"1\" value=\"0\" disabled />
              <span id=\"sensor-value-label\">0</span>
            </label>
            <label id=\"sensor-toggle-wrapper\" class=\"hidden\">
              <input type=\"checkbox\" id=\"sensor-toggle\" disabled />
              Pressed / Active
            </label>
          </div>
        </div>
      </section>

      <section class=\"panel\" id=\"status-panel\">
        <div class=\"panel-header\">
          <h2>Inputs &amp; Battery</h2>
        </div>
        <div class=\"button-grid\">
          <button class=\"ev3-btn\" data-button=\"UP\">Up</button>
          <button class=\"ev3-btn\" data-button=\"LEFT\">Left</button>
          <button class=\"ev3-btn\" data-button=\"CENTER\">Center</button>
          <button class=\"ev3-btn\" data-button=\"RIGHT\">Right</button>
          <button class=\"ev3-btn span-2\" data-button=\"DOWN\">Down</button>
        </div>
        <p id=\"pressed-buttons\">Pressed: None</p>
        <label class=\"control-line\">
          Battery voltage (V)
          <input type=\"range\" id=\"battery-slider\" min=\"5.5\" max=\"9.0\" step=\"0.1\" value=\"7.4\" />
          <span id=\"battery-value\">7.4 V</span>
        </label>
      </section>

      <section class=\"panel span-2\" id=\"console-panel\">
        <div class=\"panel-header\">
          <h2>Console</h2>
          <button id=\"clear-console\">Clear</button>
        </div>
        <div class=\"console-log\" id=\"console-log\"></div>
      </section>
    </main>
    <script src=\"/app.js\"></script>
  </body>
</html>
"""

APP_CSS = """:root {
  color-scheme: dark;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #0f1115;
  color: #f3f5f7;
}

body {
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid #20232b;
  background: #131620;
}

.app-header h1 {
  margin: 0 0 4px;
  font-size: 1.5rem;
}

.app-header p {
  margin: 0;
  color: #a3aab8;
}

.status-block {
  font-weight: 600;
  color: #7ad7ff;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 16px;
  padding: 16px;
}

.panel {
  background: #181b24;
  border: 1px solid #20232b;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.panel h2 {
  margin: 0;
  font-size: 1.1rem;
}

.table-wrapper {
  overflow: auto;
  max-height: 260px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 6px 8px;
  border-bottom: 1px solid #20232b;
  text-align: center;
  font-size: 0.9rem;
}

tbody tr:hover {
  background: #1f232f;
  cursor: pointer;
}

tbody tr.selected {
  background: #25304a;
}

.panel-footer {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-line input[type=range] {
  flex: 1;
}

.sensor-controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.sensor-controls label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hidden {
  display: none;
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.ev3-btn {
  padding: 10px;
  border: 1px solid #2d3342;
  border-radius: 6px;
  background: #212633;
  color: #f3f5f7;
  font-weight: 600;
}

.ev3-btn.active {
  background: #3a80f6;
}

.ev3-btn.span-2 {
  grid-column: span 2;
}

#console-panel {
  min-height: 300px;
}

.console-log {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #20232b;
  border-radius: 6px;
  padding: 8px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  font-size: 0.85rem;
  background: #0d0f16;
}

.console-entry {
  margin: 0;
  padding: 2px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

#clear-console {
  border: 1px solid #494f5e;
  background: transparent;
  color: #f3f5f7;
  padding: 6px 10px;
  border-radius: 6px;
}

#clear-console:hover {
  background: rgba(255, 255, 255, 0.08);
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .button-grid {
    grid-template-columns: 1fr;
  }

  .ev3-btn.span-2 {
    grid-column: span 1;
  }
}
"""

APP_JS = """const state = {
  motors: [],
  sensors: [],
  selectedMotorId: null,
  selectedSensorId: null,
  consoleSeq: 0,
  pollingHandle: null,
  pressedButtons: [],
  batteryDragging: false,
};

const motorsBody = document.getElementById('motors-body');
const sensorsBody = document.getElementById('sensors-body');
const motorDetailsEl = document.getElementById('motor-details');
const motorSpeedEl = document.getElementById('motor-speed');
const motorSpeedValueEl = document.getElementById('motor-speed-value');
const sensorDetailsEl = document.getElementById('sensor-details');
const sensorSliderWrapper = document.getElementById('sensor-slider-wrapper');
const sensorSliderEl = document.getElementById('sensor-value');
const sensorSliderValueEl = document.getElementById('sensor-value-label');
const sensorToggleWrapper = document.getElementById('sensor-toggle-wrapper');
const sensorToggleEl = document.getElementById('sensor-toggle');
const consoleEl = document.getElementById('console-log');
const statusTextEl = document.getElementById('status-text');
const pressedButtonsEl = document.getElementById('pressed-buttons');
const batterySliderEl = document.getElementById('battery-slider');
const batteryValueEl = document.getElementById('battery-value');

async function fetchState() {
  const response = await fetch(`/state?last_seq=${state.consoleSeq}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

function renderMotors() {
  if (!state.selectedMotorId && state.motors.length) {
    state.selectedMotorId = state.motors[0].id;
  }
  motorsBody.innerHTML = '';
  state.motors.forEach((motor) => {
    const row = document.createElement('tr');
    row.dataset.id = motor.id;
    if (motor.id === state.selectedMotorId) {
      row.classList.add('selected');
    }
    row.innerHTML = `
      <td>${motor.name}</td>
      <td>${motor.port}</td>
      <td>${motor.mode}</td>
      <td>${motor.command.toFixed(2)}</td>
      <td>${motor.actual_speed.toFixed(2)}</td>
      <td>${motor.angle.toFixed(2)}</td>
    `;
    row.addEventListener('click', () => selectMotor(motor.id));
    motorsBody.appendChild(row);
  });
  updateMotorControls();
}

function renderSensors() {
  sensorsBody.innerHTML = '';
  state.sensors.forEach((sensor) => {
    const row = document.createElement('tr');
    row.dataset.id = sensor.id;
    if (sensor.id === state.selectedSensorId) {
      row.classList.add('selected');
    }
    row.innerHTML = `
      <td>${sensor.name}</td>
      <td>${sensor.port}</td>
      <td>${sensor.sensor_type}</td>
      <td>${sensor.value}</td>
    `;
    row.addEventListener('click', () => selectSensor(sensor.id));
    sensorsBody.appendChild(row);
  });
  updateSensorControls();
}

function updateMotorControls() {
  const motor = state.motors.find((m) => m.id === state.selectedMotorId);
  if (!motor) {
    state.selectedMotorId = null;
    motorDetailsEl.textContent = 'None';
    motorSpeedEl.disabled = true;
    motorSpeedEl.value = 0;
    motorSpeedValueEl.textContent = '0';
    return;
  }
  motorDetailsEl.textContent = `${motor.name} on ${motor.port} (${motor.mode})`;
  motorSpeedEl.disabled = false;
  const clamped = Math.max(-1000, Math.min(1000, motor.feedback_speed));
  motorSpeedEl.value = clamped;
  motorSpeedValueEl.textContent = `${clamped.toFixed(1)} deg/s`;
}

function updateSensorControls() {
  const sensor = state.sensors.find((s) => s.id === state.selectedSensorId);
  if (!sensor) {
    state.selectedSensorId = null;
    sensorDetailsEl.textContent = 'None';
    sensorSliderEl.disabled = true;
    sensorToggleEl.disabled = true;
    sensorSliderWrapper.classList.remove('hidden');
    sensorToggleWrapper.classList.add('hidden');
    return;
  }
  sensorDetailsEl.textContent = `${sensor.name} (${sensor.sensor_type})`;
  const meta = sensor.meta || {};
  if (meta.control === 'toggle') {
    sensorSliderWrapper.classList.add('hidden');
    sensorToggleWrapper.classList.remove('hidden');
    sensorToggleEl.disabled = false;
    sensorToggleEl.checked = Boolean(sensor.value);
  } else {
    sensorToggleWrapper.classList.add('hidden');
    sensorSliderWrapper.classList.remove('hidden');
    sensorSliderEl.disabled = false;
    sensorSliderEl.min = meta.min ?? 0;
    sensorSliderEl.max = meta.max ?? 100;
    sensorSliderEl.step = meta.step ?? 1;
    sensorSliderEl.value = sensor.value;
    sensorSliderValueEl.textContent = `${sensor.value}`;
  }
}

function renderButtons(buttons) {
  const pressed = new Set(buttons);
  document.querySelectorAll('.ev3-btn').forEach((btn) => {
    const name = btn.dataset.button;
    if (pressed.has(name)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  pressedButtonsEl.textContent = pressed.size ? `Pressed: ${Array.from(pressed).join(', ')}` : 'Pressed: None';
}

function appendConsole(events) {
  if (!events.length) {
    return;
  }
  events.forEach((event) => {
    const div = document.createElement('div');
    div.className = 'console-entry';
    const level = event.level.toUpperCase().padEnd(5, ' ');
    const timestamp = event.timestamp.toFixed(2).padStart(7, ' ');
    div.textContent = `[${timestamp}s] [${level}] ${event.message}`;
    consoleEl.appendChild(div);
  });
  while (consoleEl.childElementCount > 500) {
    consoleEl.removeChild(consoleEl.firstChild);
  }
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

function updateStatus(robotRunning) {
  statusTextEl.textContent = robotRunning ? 'Robot thread: running' : 'Robot thread: stopped';
  statusTextEl.style.color = robotRunning ? '#7ad7ff' : '#f3f5f7';
}

function updateBatterySlider(voltage) {
  if (!state.batteryDragging) {
    batterySliderEl.value = voltage.toFixed(2);
  }
  batteryValueEl.textContent = `${voltage.toFixed(2)} V`;
}

function selectMotor(motorId) {
  state.selectedMotorId = motorId;
  updateMotorControls();
}

function selectSensor(sensorId) {
  state.selectedSensorId = sensorId;
  updateSensorControls();
}

async function postJSON(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
}

motorSpeedEl.addEventListener('input', (event) => {
  const value = Number(event.target.value);
  motorSpeedValueEl.textContent = `${value.toFixed(1)} deg/s`;
  if (state.selectedMotorId) {
    postJSON(`/motors/${state.selectedMotorId}/feedback`, { speed: value }).catch(() => {});
  }
});

sensorSliderEl.addEventListener('input', (event) => {
  const value = Number(event.target.value);
  sensorSliderValueEl.textContent = `${value}`;
  if (state.selectedSensorId) {
    postJSON(`/sensors/${state.selectedSensorId}`, { value }).catch(() => {});
  }
});

sensorToggleEl.addEventListener('change', (event) => {
  if (state.selectedSensorId) {
    postJSON(`/sensors/${state.selectedSensorId}`, { value: Boolean(event.target.checked) }).catch(() => {});
  }
});

batterySliderEl.addEventListener('pointerdown', () => {
  state.batteryDragging = true;
});

window.addEventListener('pointerup', () => {
  state.batteryDragging = false;
});

batterySliderEl.addEventListener('input', (event) => {
  const value = Number(event.target.value);
  batteryValueEl.textContent = `${value.toFixed(2)} V`;
  postJSON('/battery', { voltage: value }).catch(() => {});
});

document.querySelectorAll('.ev3-btn').forEach((btn) => {
  const name = btn.dataset.button;
  btn.addEventListener('pointerdown', () => postJSON(`/buttons/${name}`, { pressed: true }).catch(() => {}));
  btn.addEventListener('pointerup', () => postJSON(`/buttons/${name}`, { pressed: false }).catch(() => {}));
  btn.addEventListener('pointerleave', () => postJSON(`/buttons/${name}`, { pressed: false }).catch(() => {}));
});

document.getElementById('clear-console').addEventListener('click', () => {
  consoleEl.innerHTML = '';
});

async function pollLoop() {
  try {
    const data = await fetchState();
    state.motors = data.motors;
    state.sensors = data.sensors;
    renderMotors();
    renderSensors();
    renderButtons(data.buttons);
    appendConsole(data.console_events);
    updateStatus(data.robot_running);
    updateBatterySlider(data.battery_voltage);
    state.consoleSeq = data.console_seq;
  } catch (error) {
    statusTextEl.textContent = `UI error: ${error.message}`;
    statusTextEl.style.color = '#ff7a7a';
  } finally {
    state.pollingHandle = window.setTimeout(pollLoop, 250);
  }
}

pollLoop();

window.addEventListener('beforeunload', () => {
  navigator.sendBeacon('/shutdown', '{}');
});
"""
