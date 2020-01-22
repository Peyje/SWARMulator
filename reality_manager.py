# Import needed modules
import cflib.crtp


def scan_for_drones(gui):
	"""
	Scan for available drones.
	All channels from 0 to 125 will be scanned for addresses ranging from 0xE7E7E7E7E0 to 0xE7E7E7E7EF.
	:param gui: GUI instance to update progress bar and store found drones.
	"""
	# Load the drivers
	cflib.crtp.init_drivers(enable_debug_driver=False)

	# Create list to store found drones
	found_drones = []

	# Create list of addresses to scan for
	address_list = []
	for i in range(0x0, 0x10):
		address_list.append(0xE7E7E7E7E0 + i)

	# Create variable to store progress of task: 0 == not started & 1 == done
	progress = 0

	# Scan every channel for every address and add to the list of found drones
	for address in address_list:
		print("Start scanning for address: " + hex(address))

		# Refresh the progress bar
		progress += 1/17
		gui.update_progress_scan(progress, str(hex(address)))

		# Store found drones in a temporary list
		scan_results = cflib.crtp.scan_interfaces(address=address)

		# Append found drones to the final list
		for drone in scan_results:
			# The scanner does not append the address if it is the default one 0xE7E7E7E7E7, so we manually add it
			if address == 0xe7e7e7e7e7:
				drone[0] = drone[0] + "/E7E7E7E7E7"

			# Add drone to store of GUI
			gui.add_to_drone_store([drone[0]])

	# Final update of progress bar
	gui.update_progress_scan(1, "Done.")
