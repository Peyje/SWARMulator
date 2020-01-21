# Import needed modules
import cflib.crtp


def scan_for_drones():
	"""
	Scan for available drones.
	:return: A list of all found drones.
	"""
	found_drones = cflib.crtp.scan_interfaces()

	# TODO: Remove test uris
	found_drones.append("URI 1")
	found_drones.append("URI 2")

	return found_drones
