# Load  Panda3D modules
from direct.showbase import DirectObject
from panda3d.core import LPoint3f
from panda3d.core import LVector3f

# Load classes from other files
from drone import Drone

# Import needed modules
import csv
import random


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

		self.in_flight = False  # As drones are not started yet

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
		self.default_formation(self.drones[0].COLLISION_SPHERE_RADIUS)

		# Set them into their default formation
		for drone in self.drones:
			drone.set_pos(drone.get_target())

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
		self.in_flight = True
		for drone in self.drones:
			pos = drone.get_pos()
			drone.set_target(LPoint3f(pos[0], pos[1], 1))

	def land(self):
		"""
		Set the drones down where they are in X and Y right now.
		"""
		self.in_flight = False
		for drone in self.drones:
			pos = drone.get_pos()
			drone.set_target(LPoint3f(pos[0], pos[1], 0.1))

	def stop_movement(self):
		"""
		To stop all current movement just set the current position to the target position.
		"""
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
