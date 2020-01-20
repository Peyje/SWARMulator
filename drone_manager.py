# Load  Panda3D modules
from direct.showbase import DirectObject
from panda3d.core import Vec3

# Load classes from other files
from drone import Drone

# Import needed modules
import csv


class DroneManager(DirectObject.DirectObject):
	"""
	This class stores the simulated drones and handles all interaction with them.
	"""

	def __init__(self, base):
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

		base.taskMgr.add(update_drones_task, "UpdateDronesTask")

	def update_drone_amount(self, amount):
		"""
		Changes amount of currently loaded drones in simulation.
			:param amount: Amount of drones to be set, should be a positive integer.
		"""
		while len(self.drones) != amount:
			# Too much drones? Delete some
			if len(self.drones) > amount:
				del(self.drones[-1])
			# Not enough drones? Add some
			else:
				self.drones.append(Drone(self, Vec3(0, 0, 0), None))

		# Update their position to the default formation
		self.update_drone_positions_to_default()

	def load_formation(self, name):
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

	def update_drone_positions_to_default(self):
		"""
		Set positions of drones to a default formation set in the 'formations/2D/X_default.csv' files
		"""
		# Load the corresponding formation as a list
		formation_path = "2D/" + str(len(self.drones)) + "_default.csv"
		formation = self.load_formation(formation_path)

		# Update positions of drones
		for i in range(len(self.drones)):
			position = Vec3(formation[i][0], formation[i][1], formation[i][2])
			self.drones[i].setPos(position)  # Set positions (jump to position)
			self.drones[i].setTarget(position)  # ..but set target as well, or they would fly to their former target

	def takeoff(self):
		self.in_flight = True
		for drone in self.drones:
			pos = drone.getPos()
			drone.setTarget(target=Vec3(pos[0], pos[1], 1))

	def land(self):
		self.in_flight = False
		for drone in self.drones:
			pos = drone.getPos()
			drone.setTarget(target=Vec3(pos[0], pos[1], 0))

