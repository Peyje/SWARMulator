# Import needed modules
import cflib.crtp


def scan_for_drones():
	"""
	Scan for available drones.
	All channels from 0 to 125 will be scanned for addresses ranging from 0xE7E7E7E7E0 to 0xE7E7E7E7EF.
	:return: A list of all found drones.
	"""
	# Load the drivers
	cflib.crtp.init_drivers(enable_debug_driver=False)

	# Create list to store found drones
	found_drones = []

	# Create list of addresses to scan for
	address_list = []
	for i in range(0x0, 0xF):
		address_list.append(0xE7E7E7E7E0 + i)

	# Scan every channel for every address and add to the list of found drones
	for address in address_list:
		print("Start scanning for address: " + hex(address))
		# Store found drones in a temporary list
		scan_results = cflib.crtp.scan_interfaces(address=address)

		# Append found drones to the final list
		for drone in scan_results:
			# The scanner does not append the address if it is the default one 0xE7E7E7E7E7, so we manually add it
			if address == 0xe7e7e7e7e7:
				drone[0] = drone[0] + "/E7E7E7E7E7"
			found_drones.append(drone)

	# Log for testing
	for drone in found_drones:
		print("Found one: " + drone[0])

	return found_drones
