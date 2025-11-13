import dearpygui.dearpygui as dpg
from .state import EMU_STATE


class EmulatorUI:
	def __init__(self):
		self._initialized = False
		self._sensor_inputs = {}  # Store input field references
		self._motor_resistance_inputs = {}  # Store resistance input field references for DC mode motors

	def initialize(self):
		"""Initialize the UI window."""
		if self._initialized:
			return
		
		# Create Dear PyGui context and viewport
		dpg.create_context()
		dpg.create_viewport(title="EV3 Emulator", width=600, height=700)
		
		# Create main window that fills the viewport
		with dpg.window(label="EV3 Emulator", tag="main_window"):
			dpg.add_text("EV3 Emulator Control Panel", color=[100, 200, 255])
			dpg.add_separator()
			
			# Motors section
			with dpg.collapsing_header(label="Motors", default_open=True):
				dpg.add_text("Motor Status", tag="motors_text")
				dpg.add_group(tag="motors_resistance_container")
			
			dpg.add_separator()
			
			# Sensors section
			with dpg.collapsing_header(label="Sensors", default_open=True, tag="sensors_header"):
				dpg.add_text("Sensor Controls")
				dpg.add_group(tag="sensors_container")
			
			dpg.add_separator()
			
			# Buttons section
			with dpg.collapsing_header(label="EV3 Buttons", default_open=True, tag="buttons_header"):
				dpg.add_text("Simulate Button Presses")
				dpg.add_group(tag="buttons_container")
		
		# Configure window to fill viewport
		dpg.set_primary_window("main_window", True)
		
		dpg.setup_dearpygui()
		dpg.show_viewport()
		self._initialized = True
		
		# Initial refresh
		self.refresh()

	def process_events(self):
		"""Process UI events. Call this from pybricks functions."""
		if self._initialized:
			try:
				dpg.render_dearpygui_frame()
				# Always update motor angles (they integrate continuously)
				# Refresh display periodically (every few calls)
				if not hasattr(self, '_refresh_counter'):
					self._refresh_counter = 0
				self._refresh_counter += 1
				# Update motor angles every call, refresh display every 5 calls
				self._update_motor_angles()
				if self._refresh_counter >= 5:  # Refresh every 5 calls
					self._refresh_counter = 0
					self.refresh()
			except Exception:
				pass  # Ignore errors if window is closed
	
	def _update_motor_angles(self):
		"""Update motor angles by integrating speed over time."""
		# This triggers angle integration by accessing motors
		# get_motors() now automatically updates angles for all motors
		try:
			EMU_STATE.get_motors()  # This updates angles automatically
		except Exception:
			pass

	def refresh(self):
		"""Refresh the UI display."""
		if not self._initialized:
			return
		
		try:
			# Check for completed motor commands during refresh
			self._check_motor_commands()
			self._refresh_motors()
			self._refresh_motor_resistance_controls()
			self._refresh_sensors()
			self._refresh_buttons()
		except Exception:
			pass  # Ignore errors during refresh
	
	def _check_motor_commands(self):
		"""Check all motors for completed background commands."""
		# get_motors() already updates angles and checks completion
		motors = EMU_STATE.get_motors()
		# Additional check for command completion
		for m in motors:
			try:
				result = EMU_STATE.set_motor(m.port, power=m.power, speed=m.speed,
				                    target_speed=m.target_speed, using_run_mode=m.using_run_mode)
				# Note: Completion handling happens in Motor class methods
			except Exception:
				pass  # Ignore errors

	def _refresh_motors(self):
		"""Update motor display."""
		motors = EMU_STATE.get_motors()
		
		# Build motor status text
		if not motors:
			motor_text = "No motors detected"
		else:
			lines = []
			for m in motors:
				angle_status = f"Angle={m.angle:+7.1f}°" if m.using_run_mode else "Angle=N/A (dc mode)"
				lines.append(f"Port {m.port}: Power={m.power:+6.1f}%  Speed={m.speed:+6.1f}  {angle_status}")
			motor_text = "\n".join(lines)
		
		# Update text if tag exists
		if dpg.does_item_exist("motors_text"):
			dpg.set_value("motors_text", motor_text)
	
	def _refresh_motor_resistance_controls(self):
		"""Update motor resistance controls (only for DC mode motors)."""
		motors = EMU_STATE.get_motors()
		
		# Filter to only DC mode motors
		dc_motors = [m for m in motors if not m.using_run_mode]
		
		# Check if we need to rebuild resistance UI (motors changed or mode changed)
		current_dc_ports = {m.port for m in dc_motors}
		existing_ports = set(self._motor_resistance_inputs.keys())
		
		if current_dc_ports != existing_ports:
			# Rebuild resistance UI if DC motors changed
			if dpg.does_item_exist("motors_resistance_container"):
				dpg.delete_item("motors_resistance_container", children_only=True)
			self._motor_resistance_inputs.clear()
			
			# Create resistance controls for DC mode motors
			if not dc_motors:
				# No DC mode motors, show nothing or a message
				pass
			else:
				dpg.add_text("Motor Resistance (DC Mode Only):", parent="motors_resistance_container")
				for m in dc_motors:
					port_str = str(m.port)
					with dpg.group(horizontal=True, parent="motors_resistance_container"):
						dpg.add_text(f"Port {port_str}:")
						# Create input field for resistance
						input_tag = f"motor_resistance_{port_str}"
						
						# Create callback function with proper closure
						def make_resistance_callback(port):
							return lambda sender, app_data: self._on_motor_resistance_change(port, app_data)
						
						def make_resistance_set_callback(port):
							return lambda sender, app_data: self._on_motor_resistance_set(port)
						
						dpg.add_input_float(
							label="Resistance",
							default_value=m.resistance,
							tag=input_tag,
							width=100,
							callback=make_resistance_callback(port_str),
							on_enter=True,
							min_value=0.1,
							max_value=10.0,
							format="%.2f"
						)
						dpg.add_button(
							label="Set",
							callback=make_resistance_set_callback(port_str)
						)
						self._motor_resistance_inputs[port_str] = input_tag
		else:
			# Update existing input fields with current resistance values (but don't overwrite user input)
			# Only update if the value changed significantly (more than 0.01) to avoid interfering with user typing
			for port_str, input_tag in self._motor_resistance_inputs.items():
				if dpg.does_item_exist(input_tag):
					for m in dc_motors:
						if str(m.port) == port_str:
							current_ui_value = dpg.get_value(input_tag)
							# Only update if difference is significant (user might be typing)
							if abs(current_ui_value - m.resistance) > 0.01:
								dpg.set_value(input_tag, m.resistance)
							break
	
	def _on_motor_resistance_change(self, port, value):
		"""Handle motor resistance value change from input field (on Enter key)."""
		if port:
			try:
				resistance = float(value)
				# Clamp to reasonable range
				resistance = max(0.1, min(10.0, resistance))
				EMU_STATE.set_motor_resistance(port, resistance)
			except (ValueError, TypeError):
				pass  # Ignore invalid values
	
	def _on_motor_resistance_set(self, port):
		"""Handle motor resistance set button click."""
		if port:
			input_tag = f"motor_resistance_{port}"
			if dpg.does_item_exist(input_tag):
				try:
					value = dpg.get_value(input_tag)
					resistance = float(value)
					# Clamp to reasonable range
					resistance = max(0.1, min(10.0, resistance))
					EMU_STATE.set_motor_resistance(port, resistance)
					# Update UI to show clamped value
					dpg.set_value(input_tag, resistance)
				except (ValueError, TypeError):
					pass  # Ignore invalid values

	def _refresh_sensors(self):
		"""Update sensor display and inputs."""
		# Filter out sensors with invalid ports
		sensors = [s for s in EMU_STATE.get_sensors() if s.port and s.port != "None" and str(s.port) != "None"]
		
		# Check if we need to rebuild sensor UI (new sensors added)
		current_ports = {s.port for s in sensors}
		existing_ports = set(self._sensor_inputs.values())
		
		if current_ports != existing_ports:
			# Rebuild sensor UI if sensors changed
			if dpg.does_item_exist("sensors_container"):
				dpg.delete_item("sensors_container", children_only=True)
			self._sensor_inputs.clear()
			
			# Create new sensor UI
			if not sensors:
				dpg.add_text("No sensors detected", parent="sensors_container")
			else:
				for s in sensors:
					port_str = str(s.port)
					with dpg.group(horizontal=True, parent="sensors_container"):
						dpg.add_text(f"Port {port_str}:")
						# Create input field
						input_tag = f"sensor_input_{port_str}"
						
						# Create callback functions with proper closure
						def make_change_callback(port):
							return lambda sender, app_data: self._on_sensor_change(port, app_data)
						
						def make_set_callback(port):
							return lambda sender, app_data: self._on_sensor_set(port)
						
						dpg.add_input_float(
							label="Value",
							default_value=s.value,
							tag=input_tag,
							width=100,
							callback=make_change_callback(port_str),
							on_enter=True
						)
						dpg.add_button(
							label="Set",
							callback=make_set_callback(port_str)
						)
						self._sensor_inputs[input_tag] = port_str
		else:
			# Don't update input fields - let user control them
			# The state will reflect what the user sets via the UI
			pass

	def _on_sensor_change(self, port, value):
		"""Handle sensor value change from input field (on Enter key)."""
		if port and port != "None":
			try:
				EMU_STATE.set_sensor(port, float(value))
			except (ValueError, TypeError):
				pass  # Ignore invalid values

	def _on_sensor_set(self, port):
		"""Handle sensor set button click."""
		if port and port != "None":
			input_tag = f"sensor_input_{port}"
			if dpg.does_item_exist(input_tag):
				try:
					value = dpg.get_value(input_tag)
					EMU_STATE.set_sensor(port, float(value))
				except (ValueError, TypeError):
					pass  # Ignore invalid values

	def _refresh_buttons(self):
		"""Update button display and controls."""
		# Check if buttons UI already exists
		if not dpg.does_item_exist("buttons_container"):
			return
		
		# Check if buttons UI needs to be created
		children = dpg.get_item_children("buttons_container", slot=1)
		if children:
			# Buttons UI already exists, just update button states
			self._update_button_states()
			return
		
		# Create button controls
		button_names = ["LEFT", "RIGHT", "UP", "DOWN", "MIDDLE"]
		button_labels = {
			"LEFT": "← Left",
			"RIGHT": "Right →",
			"UP": "↑ Up",
			"DOWN": "↓ Down",
			"MIDDLE": "● Center"
		}
		
		with dpg.group(horizontal=False, parent="buttons_container"):
			dpg.add_text("Click buttons to simulate presses:", color=[200, 200, 200])
			dpg.add_spacing(count=1)
			
			# Create a grid layout for buttons
			with dpg.group(horizontal=True, parent="buttons_container"):
				dpg.add_spacing(count=1)
			with dpg.group(horizontal=True, parent="buttons_container"):
				dpg.add_spacing(count=1)
				# Up button
				up_tag = "button_UP"
				dpg.add_button(
					label=button_labels["UP"],
					tag=up_tag,
					width=100,
					height=50,
					callback=self._make_button_callback("UP")
				)
				dpg.add_spacing(count=1)
			
			with dpg.group(horizontal=True, parent="buttons_container"):
				# Left button
				left_tag = "button_LEFT"
				dpg.add_button(
					label=button_labels["LEFT"],
					tag=left_tag,
					width=100,
					height=50,
					callback=self._make_button_callback("LEFT")
				)
				# Middle button
				middle_tag = "button_MIDDLE"
				dpg.add_button(
					label=button_labels["MIDDLE"],
					tag=middle_tag,
					width=100,
					height=50,
					callback=self._make_button_callback("MIDDLE")
				)
				# Right button
				right_tag = "button_RIGHT"
				dpg.add_button(
					label=button_labels["RIGHT"],
					tag=right_tag,
					width=100,
					height=50,
					callback=self._make_button_callback("RIGHT")
				)
			
			with dpg.group(horizontal=True, parent="buttons_container"):
				dpg.add_spacing(count=1)
				# Down button
				down_tag = "button_DOWN"
				dpg.add_button(
					label=button_labels["DOWN"],
					tag=down_tag,
					width=100,
					height=50,
					callback=self._make_button_callback("DOWN")
				)
				dpg.add_spacing(count=1)
			
			dpg.add_spacing(count=1)
			dpg.add_text("Tip: Click to toggle button state", color=[150, 150, 150])
		
		# Set up button handlers for press/release (mouse down/up)
		for button_name in button_names:
			button_tag = f"button_{button_name}"
			if dpg.does_item_exist(button_tag):
				# Create handler registry for this button
				handler_tag = f"button_handler_{button_name}"
				with dpg.item_handler_registry(tag=handler_tag):
					# Mouse down - press button
					dpg.add_item_active_handler(
						callback=self._make_button_active_callback(button_name, True)
					)
					# Mouse up - release button
					dpg.add_item_deactivated_handler(
						callback=self._make_button_active_callback(button_name, False)
					)
				dpg.bind_item_handler_registry(button_tag, handler_tag)
		
		# Update button visual states
		self._update_button_states()

	def _make_button_callback(self, button_name: str):
		"""Create a callback function for button toggle."""
		def callback(sender, app_data, user_data):
			current_state = EMU_STATE.is_button_pressed(button_name)
			EMU_STATE.set_button(button_name, not current_state)
			self._update_button_states()
		return callback

	def _make_button_active_callback(self, button_name: str, pressed: bool):
		"""Create a callback function for button press/release (mouse down/up)."""
		def callback(sender, app_data, user_data):
			EMU_STATE.set_button(button_name, pressed)
			self._update_button_states()
		return callback

	def _update_button_states(self):
		"""Update visual appearance of buttons based on their pressed state."""
		button_names = ["LEFT", "RIGHT", "UP", "DOWN", "MIDDLE"]
		for button_name in button_names:
			button_tag = f"button_{button_name}"
			if dpg.does_item_exist(button_tag):
				is_pressed = EMU_STATE.is_button_pressed(button_name)
				if is_pressed:
					# Button is pressed - highlight it
					dpg.configure_item(button_tag, color=[100, 200, 100])
				else:
					# Button is not pressed - normal appearance
					dpg.configure_item(button_tag, color=[60, 60, 60])


_ui_singleton = None

def ensure_ui_started():
	global _ui_singleton
	if _ui_singleton is None:
		_ui_singleton = EmulatorUI()
		_ui_singleton.initialize()

def process_ui_events():
	"""Process UI events. Call this from pybricks functions."""
	global _ui_singleton
	if _ui_singleton:
		_ui_singleton.process_events()
