# Import needed modules
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

# Load other files
import reality_manager


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
		self.mode_switch = builder.get_object("modeSwitch")
		self.amount_drones_spinner = builder.get_object("amountDronesSpinner")
		self.amount_drones_adjustment = builder.get_object("amountDronesAdj")
		self.takeoff_toggle = builder.get_object("toggleFlightButton")
		self.stop_movement_button = builder.get_object("stopMovementButton")
		self.go_home_button = builder.get_object("goHomeButton")
		self.spiral_button = builder.get_object("spiralButton")
		self.random_button = builder.get_object("randomButton")
		self.scanned_drones_store = builder.get_object("scannedDronesStore")
		self.progress_bar_scan = builder.get_object("progressBarScan")

		# CheckButtons to choose drones
		self.drone_choosers = []
		self.drone_choosers.append(builder.get_object("droneChooser0"))
		self.drone_choosers.append(builder.get_object("droneChooser1"))
		self.drone_choosers.append(builder.get_object("droneChooser2"))
		self.drone_choosers.append(builder.get_object("droneChooser3"))
		self.drone_choosers.append(builder.get_object("droneChooser4"))
		self.drone_choosers.append(builder.get_object("droneChooser5"))
		self.drone_choosers.append(builder.get_object("droneChooser6"))
		self.drone_choosers.append(builder.get_object("droneChooser7"))
		self.drone_choosers.append(builder.get_object("droneChooser8"))
		self.drone_choosers.append(builder.get_object("droneChooser9"))


		# GUI objects of rotation menu
		self.rotation_add_x = builder.get_object("rotationAddX")
		self.rotation_add_y = builder.get_object("rotationAddY")
		self.rotation_add_cw = builder.get_object("rotationAddCW")
		self.rotation_add_speed = builder.get_object("rotationAddSpeed")
		self.add_rotation_button = builder.get_object("addRotationButton")
		self.stop_rotations = builder.get_object("stopRotationButton")

		# Store different states of GUI objects
		self.mode_state = self.mode_switch.get_active()  # True == on
		self.takeoff_toggle_state = self.takeoff_toggle.get_active()  # True == pressed
		self.amount_drones_value = self.amount_drones_adjustment.get_value()

	def update_progress_scan(self, fraction, address):
		"""
		Set the fraction of the progress bar for scanning for drones.
		:param fraction: Fraction of task done.
		:param address: Text to set for bar.
		"""
		self.progress_bar_scan.set_fraction(fraction)
		self.progress_bar_scan.set_text(address)

	def add_to_drone_store(self, drone):
		"""
		Add a drone to the drone store.
		:param drone: Drone to add.
		"""
		self.scanned_drones_store.append(drone)

	def onModeSwitchActivate(self, button, state):
		"""
		Switch mode (connection to real drones OR pure simulation) depending on switch.
		"""
		# TODO: Actually connect to reality
		self.mode_state = self.mode_switch.get_active()

		# Change GUI corresponding to state of switch
		if self.mode_state:
			self.amount_drones_spinner.set_sensitive(False)
		else:
			self.amount_drones_spinner.set_sensitive(True)

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
			self.mode_switch.set_sensitive(False)
			self.amount_drones_spinner.set_sensitive(False)
			self.stop_movement_button.set_sensitive(True)
			self.go_home_button.set_sensitive(True)
			self.spiral_button.set_sensitive(True)
			self.random_button.set_sensitive(True)
			for checkbutton in self.drone_choosers:
				checkbutton.set_sensitive(True)
			self.rotation_add_x.set_sensitive(True)
			self.rotation_add_y.set_sensitive(True)
			self.rotation_add_cw.set_sensitive(True)
			self.rotation_add_speed.set_sensitive(True)
			self.add_rotation_button.set_sensitive(True)

		else:
			Handler.drone_manager.land()
			self.takeoff_toggle.set_label("Takeoff")
			self.mode_switch.set_sensitive(True)
			if not self.mode_state:
				self.amount_drones_spinner.set_sensitive(True)
			self.stop_movement_button.set_sensitive(False)
			self.go_home_button.set_sensitive(False)
			self.spiral_button.set_sensitive(False)
			self.random_button.set_sensitive(False)
			for checkbutton in self.drone_choosers:
				checkbutton.set_sensitive(False)
			self.rotation_add_x.set_sensitive(False)
			self.rotation_add_y.set_sensitive(False)
			self.rotation_add_cw.set_sensitive(False)
			self.rotation_add_speed.set_sensitive(False)
			self.add_rotation_button.set_sensitive(False)
			self.stop_rotations.set_sensitive(False)

	def onStopMovementPress(self, button):
		Handler.drone_manager.stop_movement()
		self.stop_rotations.set_sensitive(False)

	def onStopRotationPress(self, button):
		Handler.drone_manager.stop_rotation()
		self.stop_rotations.set_sensitive(False)

	def onGoHomePress(self, button):
		Handler.drone_manager.default_formation(1)

	def onSpiralPress(self, button):
		Handler.drone_manager.spiral_formation()

	def onRandomPress(self, button):
		Handler.drone_manager.random_formation()

	def onScanPress(self, button):
		# Clear storage
		self.scanned_drones_store.clear()

		# Scan for drones in seperate thread as to not brick the GUI
		thread = threading.Thread(target=reality_manager.scan_for_drones, args=(self, ))
		thread.start()

	def onAddRotationPress(self, button):
		"""
		Add a constant rotation to the chosen drones.
		"""
		# Load values from GUI
		drones = []
		for num, checkbutton in enumerate(self.drone_choosers):
			if checkbutton.get_active():
				drones.append(num)
		origin = float(self.rotation_add_x.get_text()), float(self.rotation_add_y.get_text())
		cw = self.rotation_add_cw.get_active()
		speed = float(self.rotation_add_speed.get_text()) / 10  # Input is per second, task runs at .1 seconds

		# Call rotation into action
		Handler.drone_manager.set_rotation(drones, origin, speed, cw)

		# Set button to stop it to sensitive
		self.stop_rotations.set_sensitive(True)


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