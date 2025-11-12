import dearpygui.dearpygui as dpg
from .state import EMU_STATE


class EmulatorUI:
	def __init__(self):
		self._initialized = False
		self._sensor_inputs = {}  # Store input field references

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
			
			dpg.add_separator()
			
			# Sensors section
			with dpg.collapsing_header(label="Sensors", default_open=True, tag="sensors_header"):
				dpg.add_text("Sensor Controls")
				dpg.add_group(tag="sensors_container")
		
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
				# Refresh display periodically (every few calls)
				if not hasattr(self, '_refresh_counter'):
					self._refresh_counter = 0
				self._refresh_counter += 1
				if self._refresh_counter >= 5:  # Refresh every 5 calls
					self._refresh_counter = 0
					self.refresh()
			except Exception:
				pass  # Ignore errors if window is closed

	def refresh(self):
		"""Refresh the UI display."""
		if not self._initialized:
			return
		
		try:
			self._refresh_motors()
			self._refresh_sensors()
		except Exception:
			pass  # Ignore errors during refresh

	def _refresh_motors(self):
		"""Update motor display."""
		motors = EMU_STATE.get_motors()
		
		# Build motor status text
		if not motors:
			motor_text = "No motors detected"
		else:
			lines = []
			for m in motors:
				lines.append(f"Port {m.port}: Power={m.power:+6.1f}%  Speed={m.speed:+6.1f}")
			motor_text = "\n".join(lines)
		
		# Update text if tag exists
		if dpg.does_item_exist("motors_text"):
			dpg.set_value("motors_text", motor_text)

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
