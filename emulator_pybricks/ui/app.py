from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from emulator_pybricks.runtime import EmulatorRuntime, get_runtime
from pybricks.parameters import Button


class EmulatorApp:
    """Simple Tk UI for inspecting and manipulating the emulated EV3 state."""

    POLL_INTERVAL_MS = 120

    def __init__(self, runtime: Optional[EmulatorRuntime] = None):
        self.runtime = runtime or get_runtime()
        self.root = tk.Tk()
        self.root.title("Pybricks EV3 Emulator")
        self.root.geometry("1200x780")

        self._selected_motor_id: Optional[str] = None
        self._selected_sensor_id: Optional[str] = None
        self._last_console_seq = 0

        self._motor_speed_var = tk.DoubleVar(value=0.0)
        self._sensor_value_var = tk.DoubleVar(value=0.0)
        self._sensor_toggle_var = tk.BooleanVar(value=False)
        self._battery_var = tk.DoubleVar(
            value=self.runtime.get_battery_voltage_mv() / 1000.0
        )
        self._active_buttons_var = tk.StringVar(value="None")
        self._status_var = tk.StringVar(value="Robot thread: starting…")

        self._suspend_motor_speed_callback = False
        self._suspend_sensor_callback = False
        self._suspend_battery_callback = False

        self._build_layout()
        self._bind_events()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    # Layout helpers
    # ------------------------------------------------------------------ #
    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_motors_section(left)
        self._build_sensors_section(left)
        self._build_status_section(right)
        self._build_console_section(right)

    def _build_motors_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Motors")
        frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("name", "port", "mode", "command", "speed", "angle")
        self.motor_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=8,
        )
        headings = {
            "name": "Name",
            "port": "Port",
            "mode": "Mode",
            "command": "Command",
            "speed": "Speed (deg/s)",
            "angle": "Angle (deg)",
        }
        for column in columns:
            self.motor_tree.heading(column, text=headings[column])
            self.motor_tree.column(column, width=110, anchor="center")

        motor_scroll = ttk.Scrollbar(
            frame, orient="vertical", command=self.motor_tree.yview
        )
        self.motor_tree.configure(yscroll=motor_scroll.set)

        self.motor_tree.grid(row=0, column=0, sticky="nsew")
        motor_scroll.grid(row=0, column=1, sticky="ns")

        details = ttk.Frame(frame, padding=(0, 8, 0, 0))
        details.grid(row=1, column=0, columnspan=2, sticky="ew")
        details.columnconfigure(1, weight=1)

        ttk.Label(details, text="Selected motor:").grid(row=0, column=0, sticky="w")
        self.motor_details_var = tk.StringVar(value="None")
        ttk.Label(details, textvariable=self.motor_details_var).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(details, text="Simulated speed (deg/s):").grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        self.motor_speed_scale = ttk.Scale(
            details,
            from_=-1000,
            to=1000,
            orient="horizontal",
            variable=self._motor_speed_var,
            command=self._on_motor_speed_changed,
        )
        self.motor_speed_scale.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        ttk.Label(
            details,
            text="Used when motor is in power (dc) mode to emulate measured speed.",
            foreground="#555555",
        ).grid(row=2, column=0, columnspan=2, sticky="w")

    def _build_sensors_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Sensors")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("name", "port", "type", "value")
        self.sensor_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=8,
        )
        headings = {
            "name": "Name",
            "port": "Port",
            "type": "Type",
            "value": "Value",
        }
        for column in columns:
            self.sensor_tree.heading(column, text=headings[column])
            width = 130 if column == "name" else 90
            self.sensor_tree.column(column, width=width, anchor="center")

        sensor_scroll = ttk.Scrollbar(
            frame, orient="vertical", command=self.sensor_tree.yview
        )
        self.sensor_tree.configure(yscroll=sensor_scroll.set)

        self.sensor_tree.grid(row=0, column=0, sticky="nsew")
        sensor_scroll.grid(row=0, column=1, sticky="ns")

        controls = ttk.Frame(frame, padding=(0, 8, 0, 0))
        controls.grid(row=1, column=0, columnspan=2, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Selected sensor:").grid(row=0, column=0, sticky="w")
        self.sensor_details_var = tk.StringVar(value="None")
        ttk.Label(controls, textvariable=self.sensor_details_var).grid(
            row=0, column=1, sticky="w"
        )

        self.sensor_slider = ttk.Scale(
            controls,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self._sensor_value_var,
            command=self._on_sensor_value_changed,
        )
        self.sensor_slider.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        ttk.Label(controls, text="Value:").grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.sensor_toggle = ttk.Checkbutton(
            controls,
            text="Pressed / Active",
            variable=self._sensor_toggle_var,
            command=self._on_sensor_toggle_changed,
        )
        self.sensor_toggle.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.sensor_toggle.grid_remove()

    def _build_status_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Inputs & Status")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=0, sticky="ew")

        button_defs = [
            ("Up", Button.UP),
            ("Left", Button.LEFT),
            ("Center", Button.CENTER),
            ("Right", Button.RIGHT),
            ("Down", Button.DOWN),
        ]
        for idx, (label, button) in enumerate(button_defs):
            btn = ttk.Button(buttons_frame, text=label, width=10)
            btn.grid(row=0, column=idx, padx=4, pady=4)
            btn.bind(
                "<ButtonPress-1>",
                lambda _evt, b=button: self.runtime.set_button_state(b, True),
            )
            btn.bind(
                "<ButtonRelease-1>",
                lambda _evt, b=button: self.runtime.set_button_state(b, False),
            )
            btn.bind(
                "<Leave>",
                lambda _evt, b=button: self.runtime.set_button_state(b, False),
            )

        ttk.Label(frame, text="Pressed buttons:").grid(
            row=1, column=0, sticky="w", padx=2
        )
        ttk.Label(frame, textvariable=self._active_buttons_var).grid(
            row=2, column=0, sticky="w", padx=2
        )

        battery_frame = ttk.Frame(frame, padding=(0, 8, 0, 0))
        battery_frame.grid(row=3, column=0, sticky="ew")
        ttk.Label(battery_frame, text="Battery voltage (V):").grid(
            row=0, column=0, sticky="w"
        )
        self.battery_scale = ttk.Scale(
            battery_frame,
            from_=5.5,
            to=9.0,
            orient="horizontal",
            variable=self._battery_var,
            command=self._on_battery_changed,
        )
        self.battery_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        battery_frame.columnconfigure(1, weight=1)

        ttk.Label(frame, textvariable=self._status_var, padding=(0, 5, 0, 0)).grid(
            row=4, column=0, sticky="w"
        )

    def _build_console_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Console")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.console_text = tk.Text(
            frame,
            wrap="word",
            state="disabled",
            height=20,
            background="#121212",
            foreground="#f3f3f3",
        )
        console_scroll = ttk.Scrollbar(
            frame, orient="vertical", command=self.console_text.yview
        )
        self.console_text.configure(yscrollcommand=console_scroll.set)
        self.console_text.grid(row=0, column=0, sticky="nsew")
        console_scroll.grid(row=0, column=1, sticky="ns")

        actions = ttk.Frame(frame, padding=(0, 6, 0, 0))
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(actions, text="Clear console", command=self._clear_console).grid(
            row=0, column=0, sticky="w"
        )

    # ------------------------------------------------------------------ #
    # Event wiring
    # ------------------------------------------------------------------ #
    def _bind_events(self) -> None:
        self.motor_tree.bind("<<TreeviewSelect>>", self._on_motor_select)
        self.sensor_tree.bind("<<TreeviewSelect>>", self._on_sensor_select)

    # ------------------------------------------------------------------ #
    # Runtime polling & updates
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self._schedule_poll()
        self.root.mainloop()

    def _schedule_poll(self) -> None:
        if self.runtime.should_shutdown():
            self.root.after(10, self.root.quit)
            return
        self._refresh_runtime_state()
        self.root.after(self.POLL_INTERVAL_MS, self._schedule_poll)

    def _refresh_runtime_state(self) -> None:
        self._refresh_motors()
        self._refresh_sensors()
        self._refresh_console()
        self._refresh_buttons_and_status()

    def _refresh_motors(self) -> None:
        states = self.runtime.snapshot_motors()
        current_ids = set(self.motor_tree.get_children())
        incoming_ids = set()

        for state in states:
            motor_id = state["id"]
            incoming_ids.add(motor_id)
            values = (
                state["name"],
                state["port"],
                state["mode"],
                f"{state['command']:.2f}",
                f"{state['actual_speed']:.2f}",
                f"{state['angle']:.2f}",
            )
            if motor_id in current_ids:
                self.motor_tree.item(motor_id, values=values)
            else:
                self.motor_tree.insert("", "end", iid=motor_id, values=values)

            if self._selected_motor_id == motor_id:
                self.motor_details_var.set(
                    f"{state['name']} on {state['port']} ({state['mode']})"
                )
                if not self._suspend_motor_speed_callback:
                    self._suspend_motor_speed_callback = True
                    self._motor_speed_var.set(state["feedback_speed"])
                    self._suspend_motor_speed_callback = False

        # Remove stale entries
        for motor_id in current_ids - incoming_ids:
            self.motor_tree.delete(motor_id)
            if self._selected_motor_id == motor_id:
                self._selected_motor_id = None
                self.motor_details_var.set("None")

    def _refresh_sensors(self) -> None:
        states = self.runtime.snapshot_sensors()
        current_ids = set(self.sensor_tree.get_children())
        incoming_ids = set()

        for state in states:
            sensor_id = state["id"]
            incoming_ids.add(sensor_id)
            values = (
                state["name"],
                state["port"],
                state["sensor_type"],
                state["value"],
            )
            if sensor_id in current_ids:
                self.sensor_tree.item(sensor_id, values=values)
            else:
                self.sensor_tree.insert("", "end", iid=sensor_id, values=values)

            if self._selected_sensor_id == sensor_id:
                self._update_sensor_controls(state)

        for sensor_id in current_ids - incoming_ids:
            self.sensor_tree.delete(sensor_id)
            if self._selected_sensor_id == sensor_id:
                self._selected_sensor_id = None
                self.sensor_details_var.set("None")

    def _refresh_console(self) -> None:
        events, new_seq = self.runtime.consume_console_events(self._last_console_seq)
        if not events:
            return
        self._last_console_seq = new_seq
        self.console_text.configure(state="normal")
        for event in events:
            timestamp = f"{event['timestamp']:7.2f}s"
            level = event["level"].upper().ljust(5)
            self.console_text.insert(
                "end", f"[{timestamp}] [{level}] {event['message']}\n"
            )
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def _refresh_buttons_and_status(self) -> None:
        pressed = self.runtime.get_pressed_buttons()
        if pressed:
            labels = ", ".join(getattr(btn, "name", str(btn)) for btn in pressed)
            self._active_buttons_var.set(labels)
        else:
            self._active_buttons_var.set("None")

        voltage = self.runtime.get_battery_voltage_mv() / 1000.0
        if not self._suspend_battery_callback:
            self._suspend_battery_callback = True
            self._battery_var.set(voltage)
            self._suspend_battery_callback = False

        status = "running" if self.runtime.is_robot_running() else "stopped"
        self._status_var.set(f"Robot thread: {status}")

    # ------------------------------------------------------------------ #
    # UI callbacks
    # ------------------------------------------------------------------ #
    def _on_close(self) -> None:
        self.runtime.request_shutdown()
        self.root.quit()

    def _clear_console(self) -> None:
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

    def _on_motor_select(self, _event) -> None:
        selection = self.motor_tree.selection()
        self._selected_motor_id = selection[0] if selection else None
        if not self._selected_motor_id:
            self.motor_details_var.set("None")
            return
        for state in self.runtime.snapshot_motors():
            if state["id"] == self._selected_motor_id:
                self.motor_details_var.set(
                    f"{state['name']} on {state['port']} ({state['mode']})"
                )
                if not self._suspend_motor_speed_callback:
                    self._suspend_motor_speed_callback = True
                    self._motor_speed_var.set(state["feedback_speed"])
                    self._suspend_motor_speed_callback = False
                break

    def _on_sensor_select(self, _event) -> None:
        selection = self.sensor_tree.selection()
        self._selected_sensor_id = selection[0] if selection else None
        if not self._selected_sensor_id:
            self.sensor_details_var.set("None")
            return
        for state in self.runtime.snapshot_sensors():
            if state["id"] == self._selected_sensor_id:
                self._update_sensor_controls(state)
                break

    def _on_motor_speed_changed(self, value: str) -> None:
        if self._suspend_motor_speed_callback:
            return
        if not self._selected_motor_id:
            return
        try:
            speed = float(value)
        except ValueError:
            return
        self.runtime.set_motor_feedback(self._selected_motor_id, speed)

    def _on_sensor_value_changed(self, value: str) -> None:
        if self._suspend_sensor_callback:
            return
        if not self._selected_sensor_id:
            return
        try:
            sensor_value = float(value)
        except ValueError:
            return
        self.runtime.set_sensor_value(self._selected_sensor_id, sensor_value)

    def _on_sensor_toggle_changed(self) -> None:
        if self._suspend_sensor_callback:
            return
        if not self._selected_sensor_id:
            return
        self.runtime.set_sensor_value(
            self._selected_sensor_id, bool(self._sensor_toggle_var.get())
        )

    def _on_battery_changed(self, value: str) -> None:
        if self._suspend_battery_callback:
            return
        try:
            voltage_v = float(value)
        except ValueError:
            return
        self.runtime.set_battery_voltage_mv(int(voltage_v * 1000))

    def _update_sensor_controls(self, state: Dict[str, Any]) -> None:
        meta = state.get("meta") or {}
        self.sensor_details_var.set(f"{state['name']} ({state['sensor_type']})")

        control_type = meta.get("control", "slider")
        if control_type == "toggle":
            self.sensor_slider.grid_remove()
            self.sensor_toggle.grid()
            if not self._suspend_sensor_callback:
                self._suspend_sensor_callback = True
                self._sensor_toggle_var.set(bool(state["value"]))
                self._suspend_sensor_callback = False
        else:
            self.sensor_toggle.grid_remove()
            self.sensor_slider.grid()
            slider_min = meta.get("min", 0)
            slider_max = meta.get("max", 100)
            resolution = meta.get("step", 1)
            self.sensor_slider.configure(
                from_=slider_min,
                to=slider_max,
                length=300,
                resolution=resolution,
            )
            if not self._suspend_sensor_callback:
                self._suspend_sensor_callback = True
                self._sensor_value_var.set(state["value"])
                self._suspend_sensor_callback = False


__all__ = ["EmulatorApp"]

