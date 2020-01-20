# Import needed modules
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


class Handler(Gtk.Builder):
	"""
	Handles all input into the GUI, such as button presses.

	All on[..] functions are invoked by the GUI itself.
	"""
	# Stored to later control the camera through keypresses
	cam_control = []

	# Stored to later control the visibility switching of the bullet debug mode
	bullet_debug_node = []

	# Stored to later control the drones through GUI interaction
	drone_manager = []

	def __init__(self, builder):
		# Get GUI objects to manipulate
		self.amount_drones_spinner = builder.get_object("amountDronesSpinner")
		self.amount_drones_adjustment = builder.get_object("amountDronesAdj")
		self.takeoff_toggle = builder.get_object("toggleFlightButton")
		self.stop_movement_button = builder.get_object("stopMovementButton")
		self.go_home_button = builder.get_object("goHomeButton")
		self.spiral_button = builder.get_object("spiralButton")
		self.random_button = builder.get_object("randomButton")

		# Store different states of GUI objects
		self.takeoff_toggle_state = self.takeoff_toggle.get_active()  # True == pressed
		self.amount_drones_value = self.amount_drones_adjustment.get_value()

	def onAmountDronesChange(self, adjustment):
		"""
		Change state of corresponding variable and call function to handle this.
		"""
		self.amount_drones_value = self.amount_drones_adjustment.get_value()
		Handler.drone_manager.update_drone_amount(self.amount_drones_value)

	def onTakeoffToggle(self, button):
		"""
		Change state of corresponding variable and call function to handle this.
		"""
		self.takeoff_toggle_state = self.takeoff_toggle.get_active()

		# Change GUI corresponding to current state of flight of drones and send command to simulation
		if self.takeoff_toggle_state:
			Handler.drone_manager.takeoff()
			self.takeoff_toggle.set_label("Land")
			self.amount_drones_spinner.set_sensitive(False)
			self.stop_movement_button.set_sensitive(True)
			self.go_home_button.set_sensitive(True)
			self.spiral_button.set_sensitive(True)
			self.random_button.set_sensitive(True)

		else:
			Handler.drone_manager.land()
			self.takeoff_toggle.set_label("Takeoff")
			self.amount_drones_spinner.set_sensitive(True)
			self.stop_movement_button.set_sensitive(False)
			self.go_home_button.set_sensitive(False)
			self.spiral_button.set_sensitive(False)
			self.random_button.set_sensitive(False)

	def onStopMovementPress(self, button):
		Handler.drone_manager.stop_movement()

	def onGoHomePress(self, button):
		Handler.drone_manager.default_formation(1)

	def onSpiralPress(self, button):
		Handler.drone_manager.spiral_formation()

	def onRandomPress(self, button):
		Handler.drone_manager.random_formation()

	def onKeyPress(self, area, event):
		"""
		Called on any key press, it finds the corresponding function and calls it. Mostly used for moving the camera.
		"""
		keyname = Gdk.keyval_name(event.keyval)

		if keyname == 'w':
			Handler.cam_control.set_forward_trig(1)
		if keyname == 's':
			Handler.cam_control.set_forward_trig(-1)
		if keyname == 'a':
			Handler.cam_control.set_right_trig(-1)
		if keyname == 'd':
			Handler.cam_control.set_right_trig(1)
		if keyname == 'Shift_L':
			Handler.cam_control.set_up_trig(1)
		if keyname == 'Control_L':
			Handler.cam_control.set_up_trig(-1)
		if keyname == 'q':
			Handler.cam_control.set_heading_trig(1)
		if keyname == 'e':
			Handler.cam_control.set_heading_trig(-1)
		if keyname == 'r':
			Handler.cam_control.set_pitch_trig(1)
		if keyname == 'f':
			Handler.cam_control.set_pitch_trig(-1)

		if keyname == 'F1':
			if Handler.bullet_debug_node.isHidden():
				Handler.bullet_debug_node.show()
				Handler.drone_manager.set_debug(True)
			else:
				Handler.bullet_debug_node.hide()
				Handler.drone_manager.set_debug(False)

	def onKeyRelease(self, area, event):
		"""
		Same as onKeyPress, but called on the release of a key press.
		"""
		keyname = Gdk.keyval_name(event.keyval)

		if keyname == 'w' or keyname == 's':
			Handler.cam_control.set_forward_trig(0)
		if keyname == 'a' or keyname == 'd':
			Handler.cam_control.set_right_trig(0)
		if keyname == 'Shift_L' or keyname == 'Control_L':
			Handler.cam_control.set_up_trig(0)
		if keyname == 'q' or keyname == 'e':
			Handler.cam_control.set_heading_trig(0)
		if keyname == 'r' or keyname == 'f':
			Handler.cam_control.set_pitch_trig(0)