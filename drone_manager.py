# Load  Panda3D modules
from direct.showbase import DirectObject
from panda3d.core import LPoint3f
from panda3d.core import LVector3f

# Load Crazyflie modules
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

# Load classes from other files
from drone import Drone

# Import needed modules
import csv
import random
import math
import time


def load_formation(name):
	"""
	Loads a formation from its .csv-file.
	:param name: Folder of the formation + name of the formation
	:return: List of the positions of the formation
	"""
	path = "formations/" + name
	formation = []

	# Open file and write each position into a new element of the list
	with open(path) as csvfile:
		reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # quoting to convert to float automatically
		for row in reader:
			formation.append(row)

	return formation


def rotate_z(origin, point, angle):
	"""
	Rotate a point counterclockwise by a given angle around a given origin.
	Idea: https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
	:param origin: Tuple describing the origin of the rotation
	:param point: Point to rotate
	:param angle: Angle to rotate in degrees
	:return: Rotated point
	"""
	angle = math.radians(angle)

	ox, oy = origin
	px, py = point.x, point.y

	qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
	qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
	return LPoint3f(qx, qy, point.z)


class DroneManager(DirectObject.DirectObject):
	"""
	This class stores the simulated drones and handles all interaction with them.
	"""

	ROOM_SIZE = LVector3f(3.4, 4.56, 2.56)  # needed to calculate random positions
	TAKEOFF_HEIGHT = 1  # Default height where drones should fly to

	def __init__(self, base):
		super().__init__()
		self.base = base  # To talk to the simulation
		self.drones = []  # List of drones in simulation
		self.update_drone_amount(3)  # Start of with 3 drones

		def update_drones_task(task):
			"""
			Update every drone in the simulation.
			"""
			for drone in self.drones:
				drone.update()
			return task.cont

		# Add task to update all drones
		base.taskMgr.add(update_drones_task, "UpdateDronesTask")

	def update_drone_amount(self, amount):
		"""
		Changes amount of currently loaded drones in simulation.
			:param amount: Amount of drones to be set, should be a positive integer.
		"""
		while len(self.drones) != amount:
			# Too much drones? Delete some
			if len(self.drones) > amount:
				self.drones[-1].destroy()
				del(self.drones[-1])
			# Not enough drones? Add some
			else:
				self.drones.append(Drone(self))

		# Update their targets to the default formation
		# As to not reach into the ground: height = size of collision bounds
		if len(self.drones) > 0:
			self.default_formation(self.drones[0].COLLISION_SPHERE_RADIUS)

		# Set them into their default formation
		for drone in self.drones:
			drone.set_pos(drone.get_target())

	def connect_reality(self, uris):
		"""
		Set amount of drones to actual drones in reality and set up simulated drones to work with real ones.
		:param uris: URIs of the drones to connect to.
		"""
		# Update amount of drones to that of real drones
		self.update_drone_amount(len(uris))

		# For every drone, create SyncCrazyflie object and store it, then connect to the drone via it
		for num, drone in enumerate(self.drones):
			drone.crazyflie = SyncCrazyflie(uris[num], cf=Crazyflie(rw_cache='./cache'))
			drone.crazyflie.open_link()

	def disconnect_reality(self):
		"""
		Disconnects all real drones and sets amount to 0 (until new drones are connected or mode is set to unlink).
		"""
		# Send every drone the command to stop all rotors, then disconnect and remove object from drone
		for num, drone in enumerate(self.drones):
			drone.crazyflie.cf.commander.send_stop_setpoint()
			time.sleep(.1)  # Wait until command is sent as queue is not flushed before closing link
			drone.crazyflie.close_link()
			drone.crazyflie = None

		self.update_drone_amount(0)

	def stop_rotors(self):
		"""
		Stop all rotors of connected drones immediately and stop updating setpoint.
		"""
		for drone in self.drones:
			drone.in_flight = False  # To stop updating in update loop of drone
			if drone.crazyflie is not None:
				drone.crazyflie.cf.commander.send_stop_setpoint()
				print("STOP!")

	def set_debug(self, active):
		"""
		De-/active debugging for all drones.
		:param active: If debugging should be turned on or off.
		"""
		for drone in self.drones:
			drone.set_debug(active)

	def default_formation(self, height):
		"""
		Set target of drones to the default formation set in the 'formations/2D/X_default.csv' files
		:param height: Height of drones in formation
		"""
		# Load the corresponding formation as a list
		formation_path = "2D/" + str(len(self.drones)) + "_default.csv"
		formation = load_formation(formation_path)

		# Update positions of drones
		for i in range(len(self.drones)):
			position_in_formation = LPoint3f(formation[i][0], formation[i][1], height)
			self.drones[i].set_target(position_in_formation)

	def takeoff(self):
		"""
		Let the drones takeoff to one meter above their current position.
		"""
		for drone in self.drones:
			drone.in_flight = True
			pos = drone.get_pos()
			drone.set_target(LPoint3f(pos[0], pos[1], 1))

	def land(self):
		"""
		Set the drones down where they are in X and Y right now.
		"""
		# Stop rotations, if there are any
		self.stop_rotation()

		for drone in self.drones:
			pos = drone.get_pos()
			drone.set_target(LPoint3f(pos[0], pos[1], 0.1))

		time.sleep(1)
		for drone in self.drones:
			drone.in_flight = False

	def stop_movement(self):
		"""
		To stop all current movement just set the current position to the target position.
		"""
		self.stop_rotation()
		for drone in self.drones:
			pos = drone.get_pos()
			drone.set_target(LPoint3f(pos[0], pos[1], pos[2]))

	def random_formation(self):
		"""
		Set targets of all drones to a random position within safe corridor of room.
		"""
		# Only use part of the room as possible coordinates
		safe_coordinates = self.ROOM_SIZE - LVector3f(1.0, 1.0, 0.5)

		for drone in self.drones:
			x = random.uniform(-safe_coordinates.x / 2, safe_coordinates.x / 2)
			y = random.uniform(-safe_coordinates.y / 2, safe_coordinates.y / 2)
			z = random.uniform(0.3, safe_coordinates.z)
			drone.set_target(LPoint3f(x, y, z))

	def spiral_formation(self):
		"""
		Set target of drones to the spiral formation set in the 'formations/3D/spirals/X_spiral.csv' files
		"""
		# Load the corresponding formation as a list
		formation_path = "3D/spirals/" + str(len(self.drones)) + "_spiral.csv"
		formation = load_formation(formation_path)

		# Update positions of drones
		for i in range(len(self.drones)):
			position_in_formation = LPoint3f(formation[i][0], formation[i][1], formation[i][2])
			self.drones[i].set_target(position_in_formation)

	def set_rotation(self, drones, origin, speed, clockwise):
		"""
		Add a rotation task as wanted. See task for param doc.
		"""
		self.base.taskMgr.doMethodLater(0.1, self._set_rotation_task, "RotationTask", extraArgs=[drones, origin, speed, clockwise], appendTask=True)

	def set_movement(self, drones, x, y, z):
		"""
		Set a new target for multiple drones.
		:param drones: Drones to move.
		:param x: Relative X movement
		:param y: Relative Y movement
		:param z: Relative Z movement
		"""
		for i in drones:
			# Get current target
			current_target = self.drones[i].get_target()

			# Add relative movement
			current_target.x += x
			current_target.y += y
			current_target.z += z

			# Set new target
			self.drones[i].set_target(current_target)

	def _set_rotation_task(self, drones, origin, speed, clockwise, task):
		"""
		Add a task add a constant rotation to certain drones.
		:param drones: Which drones should join the rotation.
		:param origin: Origin for rotation.
		:param speed: XXX
		:param clockwise: If rotation should go clockwise.
		"""
		# Invert speed if clockwise is wanted (default is mathematically positive)
		if clockwise:
			speed = -speed

		for i in drones:
			# Get current target
			current_target = self.drones[i].get_target()

			# Calculate new target
			new_target = rotate_z(origin, current_target, speed)

			# Set new target
			self.drones[i].set_target(new_target)

		return task.again

	def stop_rotation(self):
		"""
		Stop all rotations
		"""
		self.base.taskMgr.remove("RotationTask")
