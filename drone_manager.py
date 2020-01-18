# Load  Panda3D modules
from direct.showbase import DirectObject


class DroneManager(DirectObject.DirectObject):
	"""
	This class stores the simulated drones and handles all interaction with them.
	"""

	def __init__(self, base):
		self.drones = []

	def update_drone_amount(self, amount):
		"""
		Changes amount of currently loaded drones in simulation.
			:param amount: Amount of drones to be set, should be a positive integer.
		"""
		print(amount)