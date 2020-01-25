# SWARMulator
This simulation makes it possible to control multiple UAVs (hence the 'swarm' in the name) in a simulation at once.
It makes use of a Panda3D scene (with the Bullet physics engine running in the background) embedded in a GTK GUI to display, calculate and control the simulation.

The main feature is the possibility to connect the simulation to [Crazyflie](https://www.bitcraze.io/crazyflie-2-1/) UAVs and control them directly through the simulation.

**This is a work in progress. Expect changes and functions which are not yet implemented.**


## Installation
**This installation is written for Ubuntu 19.04, but it should work on other versions or even OSs without much hassle.**
A running version of *Python3* is expected.

### Clone this repository
```
git clone git@github.com:Peyje/swarmulator.git
cd swarmulator
```

### Install Python requirements
```
pip3 install -r requirements.txt
```

## Run the simulation
```
python3 simulation.py
```

## Understanding the program and its modes
There are four main panels of the GUI, the **Panda3D Simulation Panel**, the **Mode Panel**, the **Control Panel** and the **Reality** Panel.

The **Simulation Panel** is self explanatory, it is technically just a *Drawing Area* that Panda3D uses as a parent frame to display the simulation.

Next is the **Mode Panel**, here you can switch between the two modes of this program. Either set up the amount of drones manually and just try the virtual simulation by itself, or update the simulation corresponding to the actual amount of drones connected.

To connect drones, you use the **Reality Panel**. Here you can scan for drones (see the *Misc* chapter for more info on that), connect to the found drones and disconnect them as well. While exiting the program stops all rotors and disconnects the drones it is advised to that manually before exiting, just to make sure.

Last is the **Control Panel** to let the drones (either just the virtual ones or the real ones as well, if you connected to some before) take off and land, move into different formations (the correct formation for the current amount of drones is automatically loaded), move drones relative to their current position and add constant rotations to the formation as well.
Here, you can also stop all movement and set the target position to their current positions to hover or immediately stop all rotors from spinning (while also resetting the simulation). 

### Camera Control
To move the camera and control the simulation, use these keybindings:

**W**: Move camera forward 

**S**: Move camera backward

**A**: Move camera left

**D**: Move camera right

**Shift**: Move camera up

**Control**: Move camera down

**Q**: Rotate camera mathematically positive around Z 

**E**: Rotate camera mathematically negative around Z 

**R**: Rotate camera mathematically negative around X 

**F**: Rotate camera mathematically positive around X

**F1**: Show debug information such as force lines and hitboxes

*Reset Camera* Button: The simulation window also has a *Reset Camera* button to reset the camera  

### Program Files
A short explanation for the most important files and folders of this program.

#### simulator.py
The main file of this program. It mainly sets the Panda3d simulation up. It also loads the GTK GUI, creates tasks to update the simulation and pyhsics engine and handles the exiting of the program. 

#### handler.py
This file handles everything that has to do with the GUI. It stores the GUI objects, updates them as needed and handles all inputs (both GUI and keyboard events). This program (at least tries to) follow the Model-View-Control scheme, so the handler.py does not directly command the drones, but calls the other classes to do that.

Some functions may also be called from other classes so that the GUI represents the current state of the simulation and its parts (e. g. a progress bar for scanning for drones).

#### reality_manager.py
This file contains functions that do not directly have to do with the simulation, e. g. the scanning for drones. It does not need to instantiated, all functions are static. Managing the real drones connected to the simulation is NOT done here, but by the *drone_manager.py*.

#### drone_manager.py
A *drone_manager* object is created as the simulation is started. This object stores all drones and commands them as a swarm. Some examples are the takeoff, flying into formation and creating tasks to be able to add constant rotations to the formation. It also invokes the updating for every single drone.

If the mode is set to link to reality, this object also handles the connect and disconnect of those real drones. 

#### drone.py
Each drone in the simulation is an object of this class (of this file). They are both created and destroyed by a *drone_manger* as well as handled by it. You can directly set and get the position and target position of each drone (or the *drone_manager* does that for the wanted formations automatically).

If real drones are connected each drone object contains a *crazyflie* object of the type *cflib.crazyflie.syncCrazyflie*. With this commands can be sent to the corresponding real drone.

* *Virtual drones*: Every update cycle (invoked by the *drone_manger*) the forces needed to get to the target are calculated and applied.
* *Real drones*: If real drones are connected every update cycle sends a command to update the target position of the real drones to the current position of the virtual drones.

#### layout.glade
The GUI layout. The GUI is a made with GTK3+ and the GUI is designed with the Glade program.

#### /models
All models for the simulation (currently the room and the drones) are stored here as an .egg file. 

One way to create new models is to design them in *Blender*, export them as a .x file and convert them to a .egg file.

#### /formations
The formations for drones, stored as .csv files. Each row is a position for a drone, and each row can be read as X, Y, Z.


## Misc
Some various information about the program.

### Scanning
Crazyflie drones have two main variables that need to be considered to be able to connect to it. First is the channel, the actual frequency the drone communicates on with the radio. The default scan of the *cflib* automatically scans all 125 different channels.

However, each Crazyflie also has an address. This address is normally set to the default of 0xE7E7E7E7E7. If you wish to work with multiple drones you probably want to have some drones on the same channel, so you vary the addresses. As there are 2^40 different possible addresses it is not really feasible to scan for all possible ones.

Instead, this program scans for addresses in the range of (0xE7E7E7E7E0, 0xE7E7E7E7EF) on all possible channels.