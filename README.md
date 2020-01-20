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

## Documentation
Still to come..