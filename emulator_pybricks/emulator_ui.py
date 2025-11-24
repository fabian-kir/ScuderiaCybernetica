"""
Emulator UI using Tkinter

Provides a simple UI to monitor and control the emulated EV3 robot.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Dict
from .emulator_state import emulator_state, MotorMode


class EmulatorUI:
    """
    Tkinter-based UI for the EV3 emulator.
    
    Displays:
    - Motors with their modes and values
    - Sensors with editable values
    - Console output
    - Button controls
    """
    
    def __init__(self):
        self.root = None
        self.running = False
        self.update_interval = 100  # ms
        
        # UI components
        self.motor_labels: Dict[str, Dict[str, tk.Label]] = {}
        self.sensor_controls: Dict[str, Dict] = {}
        self.console_text = None
        self.led_label = None
        
    def start(self):
        """Start the UI in a separate thread"""
        if not self.running:
            self.running = True
            ui_thread = threading.Thread(target=self._run_ui, daemon=True)
            ui_thread.start()
    
    def _run_ui(self):
        """Run the Tkinter UI"""
        self.root = tk.Tk()
        self.root.title("EV3 Pybricks Emulator")
        self.root.geometry("900x700")
        
        # Register state callback
        emulator_state.register_ui_callback(self._schedule_update)
        
        # Create UI layout
        self._create_ui()
        
        # Start periodic update
        self._update_ui()
        
        # Run main loop
        self.root.mainloop()
        self.running = False
    
    def _create_ui(self):
        """Create the UI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Left panel: Motors and Sensors
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Motors section
        motors_frame = ttk.LabelFrame(left_panel, text="Motors", padding="10")
        motors_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.motors_container = motors_frame
        
        # Sensors section
        sensors_frame = ttk.LabelFrame(left_panel, text="Sensors", padding="10")
        sensors_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.sensors_container = sensors_frame
        
        # Buttons section
        buttons_frame = ttk.LabelFrame(left_panel, text="EV3 Buttons", padding="10")
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self._create_button_controls(buttons_frame)
        
        # Hub status section
        hub_frame = ttk.LabelFrame(left_panel, text="Hub Status", padding="10")
        hub_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N))
        self._create_hub_status(hub_frame)
        
        # Right panel: Console
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        
        console_frame = ttk.LabelFrame(right_panel, text="Console Output", padding="10")
        console_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.rowconfigure(0, weight=1)
        console_frame.columnconfigure(0, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame, 
            wrap=tk.WORD, 
            width=50, 
            height=30,
            font=('Courier', 9)
        )
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear console button
        clear_btn = ttk.Button(console_frame, text="Clear Console", command=self._clear_console)
        clear_btn.grid(row=1, column=0, pady=(5, 0))
    
    def _create_button_controls(self, parent):
        """Create EV3 button simulation controls"""
        # Create button layout matching EV3
        #     UP
        # LEFT CENTER RIGHT
        #     DOWN
        
        button_config = [
            ("UP", 0, 1),
            ("LEFT", 1, 0),
            ("CENTER", 1, 1),
            ("RIGHT", 1, 2),
            ("DOWN", 2, 1)
        ]
        
        for btn_name, row, col in button_config:
            btn = tk.Button(
                parent,
                text=btn_name,
                width=10,
                height=2
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            # Bind press and release events
            btn.bind('<ButtonPress-1>', lambda e, name=btn_name: self._on_button_press(name))
            btn.bind('<ButtonRelease-1>', lambda e, name=btn_name: self._on_button_release(name))
    
    def _create_hub_status(self, parent):
        """Create hub status display"""
        # LED status
        led_frame = ttk.Frame(parent)
        led_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(led_frame, text="Button LED:").grid(row=0, column=0, sticky=tk.W)
        self.led_label = ttk.Label(led_frame, text="OFF", foreground="gray")
        self.led_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Battery voltage
        battery_frame = ttk.Frame(parent)
        battery_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(battery_frame, text="Battery:").grid(row=0, column=0, sticky=tk.W)
        self.battery_label = ttk.Label(battery_frame, text="8.0V")
        self.battery_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
    
    def _on_button_press(self, button_name: str):
        """Handle button press"""
        emulator_state.press_button(button_name)
    
    def _on_button_release(self, button_name: str):
        """Handle button release"""
        emulator_state.release_button(button_name)
    
    def _clear_console(self):
        """Clear the console"""
        with emulator_state._state_lock:
            emulator_state.console_buffer.clear()
        self.console_text.delete(1.0, tk.END)
    
    def _schedule_update(self):
        """Schedule a UI update (called from state changes)"""
        if self.root and self.running:
            try:
                self.root.after(0, self._update_ui_content)
            except:
                pass
    
    def _update_ui(self):
        """Periodic UI update"""
        if not self.running:
            return
        
        self._update_ui_content()
        
        # Schedule next update
        if self.root:
            self.root.after(self.update_interval, self._update_ui)
    
    def _update_ui_content(self):
        """Update UI with current state"""
        if not self.root:
            return
        
        try:
            # Update motors
            self._update_motors_display()
            
            # Update sensors
            self._update_sensors_display()
            
            # Update console
            self._update_console()
            
            # Update hub status
            self._update_hub_status()
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def _update_motors_display(self):
        """Update motors display"""
        with emulator_state._state_lock:
            motors = emulator_state.motors.copy()
        
        # Remove motors that no longer exist
        for port in list(self.motor_labels.keys()):
            if port not in motors:
                # Remove from UI
                for widget in self.motor_labels[port].values():
                    if hasattr(widget, 'destroy'):
                        widget.destroy()
                del self.motor_labels[port]
        
        # Add or update motors
        for i, (port, motor_data) in enumerate(motors.items()):
            if port not in self.motor_labels:
                # Create new motor display
                self._create_motor_display(port, i)
            
            # Update values
            labels = self.motor_labels[port]
            labels['mode'].config(text=f"Mode: {motor_data['mode'].value}")
            labels['angle'].config(text=f"Angle: {motor_data['angle']:.1f}°")
            labels['speed'].config(text=f"Speed: {motor_data['speed']:.1f}°/s")
            
            # Show control value based on mode
            mode = motor_data['mode']
            if mode == MotorMode.DC:
                labels['control'].config(text=f"DC: {motor_data['dc_value']:.2f}")
            elif mode == MotorMode.RUN:
                labels['control'].config(text=f"Target: {motor_data['target_speed']:.1f}°/s")
            elif mode == MotorMode.TRACK_TARGET:
                labels['control'].config(text=f"Target: {motor_data['target_angle']:.1f}°")
            else:
                labels['control'].config(text="")
            
            # Allow editing speed when in DC mode (as requested)
            if mode == MotorMode.DC and 'speed_entry' in labels:
                labels['speed_entry'].config(state='normal')
            elif 'speed_entry' in labels:
                labels['speed_entry'].config(state='disabled')
    
    def _create_motor_display(self, port: str, index: int):
        """Create display for a motor"""
        frame = ttk.Frame(self.motors_container, relief=tk.RIDGE, borderwidth=1, padding="5")
        frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=2)
        
        labels = {}
        
        # Port name
        port_label = ttk.Label(frame, text=f"Port {port}:", font=('TkDefaultFont', 9, 'bold'))
        port_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        labels['port'] = port_label
        
        # Mode
        mode_label = ttk.Label(frame, text="Mode: idle")
        mode_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        labels['mode'] = mode_label
        
        # Angle
        angle_label = ttk.Label(frame, text="Angle: 0°")
        angle_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        labels['angle'] = angle_label
        
        # Speed with editable control for DC mode
        speed_frame = ttk.Frame(frame)
        speed_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        speed_label = ttk.Label(speed_frame, text="Speed: 0°/s")
        speed_label.pack(side=tk.LEFT)
        labels['speed'] = speed_label
        
        # Speed input for DC mode
        speed_entry_frame = ttk.Frame(speed_frame)
        speed_entry_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(speed_entry_frame, text="Set:").pack(side=tk.LEFT)
        speed_entry = ttk.Entry(speed_entry_frame, width=8, state='disabled')
        speed_entry.pack(side=tk.LEFT, padx=(2, 0))
        labels['speed_entry'] = speed_entry
        
        def set_speed():
            try:
                speed = float(speed_entry.get())
                emulator_state.update_motor(port, speed=speed)
            except ValueError:
                pass
        
        set_btn = ttk.Button(speed_entry_frame, text="Set", command=set_speed, width=5)
        set_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Control value
        control_label = ttk.Label(frame, text="")
        control_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        labels['control'] = control_label
        
        self.motor_labels[port] = labels
    
    def _update_sensors_display(self):
        """Update sensors display"""
        with emulator_state._state_lock:
            sensors = emulator_state.sensors.copy()
        
        # Remove sensors that no longer exist
        for port in list(self.sensor_controls.keys()):
            if port not in sensors:
                for widget in self.sensor_controls[port].values():
                    if hasattr(widget, 'destroy'):
                        widget.destroy()
                del self.sensor_controls[port]
        
        # Add or update sensors
        for i, (port, sensor_data) in enumerate(sensors.items()):
            if port not in self.sensor_controls:
                self._create_sensor_control(port, sensor_data['type'], i)
            
            # Update current value display (not the input)
            controls = self.sensor_controls[port]
            sensor_type = sensor_data['type']
            value = sensor_data['value']
            
            if sensor_type == "TouchSensor":
                controls['value_label'].config(text=f"Pressed: {value}")
            elif sensor_type == "ColorSensor":
                controls['value_label'].config(text=f"Reflection: {value}%")
            elif sensor_type == "UltrasonicSensor":
                controls['value_label'].config(text=f"Distance: {value}mm")
    
    def _create_sensor_control(self, port: str, sensor_type: str, index: int):
        """Create control for a sensor"""
        frame = ttk.Frame(self.sensors_container, relief=tk.RIDGE, borderwidth=1, padding="5")
        frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=2)
        
        controls = {}
        
        # Sensor name
        name_label = ttk.Label(frame, text=f"{sensor_type} (Port {port}):", font=('TkDefaultFont', 9, 'bold'))
        name_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        controls['name'] = name_label
        
        # Current value
        value_label = ttk.Label(frame, text="Value: -")
        value_label.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        controls['value_label'] = value_label
        
        # Control based on sensor type
        if sensor_type == "TouchSensor":
            # Toggle button for touch sensor
            def toggle_touch():
                current = emulator_state.sensors[port]['value']
                emulator_state.set_sensor_value(port, not current)
            
            btn = ttk.Button(frame, text="Toggle Press", command=toggle_touch)
            btn.grid(row=2, column=0, columnspan=3, pady=(5, 0))
            controls['button'] = btn
        
        elif sensor_type == "ColorSensor":
            # Slider for reflection (0-100)
            ttk.Label(frame, text="Set reflection:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
            
            slider = ttk.Scale(
                frame,
                from_=0,
                to=100,
                orient=tk.HORIZONTAL,
                command=lambda v: emulator_state.set_sensor_value(port, int(float(v)))
            )
            slider.set(emulator_state.sensors[port]['value'])
            slider.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
            controls['slider'] = slider
        
        elif sensor_type == "UltrasonicSensor":
            # Entry for distance
            ttk.Label(frame, text="Set distance (mm):").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
            
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, str(emulator_state.sensors[port]['value']))
            entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
            controls['entry'] = entry
            
            def set_distance():
                try:
                    distance = int(entry.get())
                    emulator_state.set_sensor_value(port, distance)
                except ValueError:
                    pass
            
            btn = ttk.Button(frame, text="Set", command=set_distance)
            btn.grid(row=2, column=2, pady=(5, 0), padx=(5, 0))
            controls['button'] = btn
        
        self.sensor_controls[port] = controls
    
    def _update_console(self):
        """Update console output"""
        if self.console_text:
            console_text = emulator_state.get_console_text()
            
            # Only update if changed
            current = self.console_text.get(1.0, tk.END).strip()
            if current != console_text:
                self.console_text.delete(1.0, tk.END)
                self.console_text.insert(1.0, console_text)
                self.console_text.see(tk.END)
    
    def _update_hub_status(self):
        """Update hub status display"""
        with emulator_state._state_lock:
            led_color = emulator_state.hub_state['button_led_color']
            battery_mv = emulator_state.hub_state['battery_voltage']
        
        # Update LED
        if led_color:
            color_name = str(led_color)
            self.led_label.config(text=color_name.upper(), foreground="green")
        else:
            self.led_label.config(text="OFF", foreground="gray")
        
        # Update battery
        battery_v = battery_mv / 1000.0
        self.battery_label.config(text=f"{battery_v:.1f}V")
    
    def stop(self):
        """Stop the UI"""
        self.running = False
        if self.root:
            self.root.quit()


# Global UI instance
emulator_ui = EmulatorUI()

