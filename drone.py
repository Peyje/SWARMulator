# Load  Panda3D modules
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.core import LPoint3f
from panda3d.core import LVector3f
from panda3d.core import LineSegs


class Drone:
    """
    Class for a single drone in the simulation.
    """

    RIGID_BODY_MASS = 0.5  # Mass of physics object
    COLLISION_SPHERE_RADIUS = 0.1  # Radius of the bullet collision sphere around the drone
    FRICTION = 0  # No friction between drone and objects, not really necessary
    # SENSORRANGE = 0.6
    TARGET_FORCE_MULTIPLIER = 1  # Allows to change influence of the force applied to get to the target
    # AVOIDANCEFORCE = 10
    TARGET_PROXIMITY_RADIUS = .5  # Drone reduces speed when in proximity of a target

    # TODO: Check if other values are better here (and find out what they really do as well..)
    LINEAR_DAMPING = 0.95
    LINEAR_SLEEP_THRESHOLD = 0

    def __init__(self, manager):
        """
        Initialises the drone as a bullet and panda object.
        :param manager: The drone manager creating this very drone.
        """
        self.manager = manager  # Drone manager handling this drone
        self.base = manager.base  # Simulation
        self.uri = None  # URI of real drone, if connected to one

        # Create bullet rigid body for drone
        drone_collision_shape = BulletSphereShape(self.COLLISION_SPHERE_RADIUS)
        self.drone_node_bullet = BulletRigidBodyNode("RigidSphere")
        self.drone_node_bullet.addShape(drone_collision_shape)
        self.drone_node_bullet.setMass(self.RIGID_BODY_MASS)

        # Set some values for the physics object
        self.drone_node_bullet.setLinearSleepThreshold(self.LINEAR_SLEEP_THRESHOLD)
        self.drone_node_bullet.setFriction(self.FRICTION)
        self.drone_node_bullet.setLinearDamping(self.LINEAR_DAMPING)

        # Attach to the simulation
        self.drone_node_panda = self.base.render.attachNewNode(self.drone_node_bullet)

        # ...and physics engine
        self.base.world.attachRigidBody(self.drone_node_bullet)

        # Add a model to the drone to be actually seen in the simulation
        drone_model = self.base.loader.loadModel("models/drones/drone_florian.egg")
        drone_model.setScale(0.2)
        drone_model.reparentTo(self.drone_node_panda)

        # Set the position and target position to their default (origin)
        default_position = LPoint3f(0, 0, 0)
        self.drone_node_panda.setPos(default_position)
        self.target_position = default_position

        # Create a line renderer to draw a line from center to target point
        self.line_creator = LineSegs()
        # Then draw a default line so that the update function works as expected (with the removal)
        self.target_line_node = self.base.render.attachNewNode(self.line_creator.create(False))

    def get_pos(self) -> LPoint3f:
        """
        Get the position of the drone.
        :return: Position of the drone as an LPoint3 object
        """
        return self.drone_node_panda.getPos()

    def set_pos(self, position: LPoint3f):
        """
        Set position of the drone.
        This directly sets the drone to that position, without any transition or flight.
        :param position: The position the drone is supposed to be at.
        """
        self.drone_node_panda.setPos(position)

    def get_target(self) -> LPoint3f:
        """
        Get the current target position of the drone.
        :return: The target position as a LPoint3 object.
        """
        return self.target_position

    def set_target(self, position: LPoint3f):
        """
        Set the target position of the drone.
        :param position: The target position to be set.
        """
        self.target_position = position

    def update(self):
        """
        Update the drone and its forces.
        """
        # Update the force needed to get to the target
        self._update_target_force()

        # Update the line drawn to the current target
        self._draw_target_line()

    def _update_target_force(self):
        """
        Calculates force needed to get to the target and applies it.
        """
        distance = (self.get_target() - self.get_pos())  # Calculate distance to fly

        # Normalise distance to get an average force for all drones, unless in close proximity of target,
        # then slowing down is encouraged and the normalisation is no longer needed
        # If normalisation would always take place overshoots would occur
        if distance > self.TARGET_PROXIMITY_RADIUS:
            distance = distance.normalized()

        # Apply to drone (with force multiplier in mind)
        self.drone_node_bullet.applyCentralForce(distance * self.TARGET_FORCE_MULTIPLIER)

    def destroy(self):
        """
        Detach drone from the simulation and physics engine, then destroy object.
        """
        self.drone_node_panda.removeNode()
        self.base.world.removeRigidBody(self.drone_node_bullet)
        self.target_line_node.removeNode()

    def _draw_target_line(self):
        """
        Draw a line from the center to the target position in the simulation.
        """
        # Remove the former line
        self.target_line_node.removeNode()

        # Create a new one
        self.line_creator.setColor(0.0, 1.0, 0.0, 1.0)
        self.line_creator.moveTo(self.get_pos())
        self.line_creator.drawTo(self.target_position)
        line = self.line_creator.create(False)

        # And attach it to the renderer
        self.target_line_node = self.base.render.attachNewNode(line)
