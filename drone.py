# TODO: REFACTOR THIS HOLE FILE

import time
import math
import random

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

from panda3d.core import Vec3
from panda3d.core import BitMask32
from panda3d.core import LineSegs
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletGhostNode


class Drone:

    # RIGIDBODYMASS = 1
    # RIGIDBODYRADIUS = 0.1
    # LINEARDAMPING = 0.97
    # SENSORRANGE = 0.6
    # TARGETFORCE = 3
    # AVOIDANCEFORCE = 25
    # FORCEFALLOFFDISTANCE = .5

    RIGIDBODYMASS = 0.5
    RIGIDBODYRADIUS = 0.1
    LINEARDAMPING = 0.95
    SENSORRANGE = 0.6
    TARGETFORCE = 1
    AVOIDANCEFORCE = 10
    FORCEFALLOFFDISTANCE = .5

    def __init__(self, manager, position: Vec3, uri="-1", printDebugInfo=False):

        self.base = manager.base
        self.manager = manager

        # The position of the real drone this virtual drone is connected to.
        # If a connection is active, this value is updated each frame.
        self.realDronePosition = Vec3(0, 0, 0)

        self.canConnect = False  # true if the virtual drone has a uri to connect to a real drone
        self.isConnected = False  # true if the connection to a real drone is currently active
        self.uri = uri
        if self.uri != "-1":
            self.canConnect = True

        self.randVec = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))

        # add the rigidbody to the drone, which has a mass and linear damping
        self.rigidBody = BulletRigidBodyNode("RigidSphere")  # derived from PandaNode
        self.rigidBody.setMass(self.RIGIDBODYMASS)  # body is now dynamic
        self.rigidBody.addShape(BulletSphereShape(self.RIGIDBODYRADIUS))
        self.rigidBody.setLinearSleepThreshold(0)
        self.rigidBody.setFriction(0)
        self.rigidBody.setLinearDamping(self.LINEARDAMPING)
        self.rigidBodyNP = self.base.render.attachNewNode(self.rigidBody)
        self.rigidBodyNP.setPos(position)
        # self.rigidBodyNP.setCollideMask(BitMask32.bit(1))
        self.base.world.attach(self.rigidBody)

        # add a 3d model to the drone to be able to see it in the 3d scene
        model = self.base.loader.loadModel(self.base.modelDir + "/drones/drone1.egg")
        model.setScale(0.2)
        model.reparentTo(self.rigidBodyNP)

        self.target = position  # the long term target that the virtual drones tries to reach
        self.setpoint = position  # the immediate target (setpoint) that the real drone tries to reach, usually updated each frame
        self.waitingPosition = Vec3(position[0], position[1], 0.7)

        self.printDebugInfo = printDebugInfo
        if self.printDebugInfo:  # put a second drone model on top of drone that outputs debug stuff
            model = self.base.loader.loadModel(self.base.modelDir + "/drones/drone1.egg")
            model.setScale(0.4)
            model.setPos(0, 0, .2)
            model.reparentTo(self.rigidBodyNP)

        # initialize line renderers
        self.targetLineNP = self.base.render.attachNewNode(LineSegs().create())
        self.velocityLineNP = self.base.render.attachNewNode(LineSegs().create())
        self.forceLineNP = self.base.render.attachNewNode(LineSegs().create())
        self.actualDroneLineNP = self.base.render.attachNewNode(LineSegs().create())
        self.setpointNP = self.base.render.attachNewNode(LineSegs().create())


    def connect(self):
        """Connects the virtual drone to a real one with the uri supplied at initialization."""
        if not self.canConnect:
            return
        print(self.uri, "connecting")
        self.isConnected = True
        self.scf = SyncCrazyflie(self.uri, cf=Crazyflie(rw_cache='./cache'))
        self.scf.open_link()
        self._reset_estimator()
        self.start_position_printing()

        # MOVE THIS BACK TO SENDPOSITIONS() IF STUFF BREAKS
        self.scf.cf.param.set_value('flightmode.posSet', '1')


    def sendPosition(self):
        """Sends the position of the virtual drone to the real one."""
        cf = self.scf.cf

        # position + the negative of the distance to the real drone
        # diff = self.getPos() - self.actualDronePosition
        # self.setpoint = self.getPos() + diff

        #  position + some function of the velocity vector
        # vel = self.getVel().length()
        # multiplier = 0.5 * (math.tanh(4 * vel - 3) + 1)
        # # pos = self.getPos() + self.getVel() * multiplier
        # self.setpoint = self.getPos() + self.getVel() * 0.5 * multiplier

        # position only
        self.setpoint = self.getPos()
        # print('Sending position {} | {} | {}'.format(self.setpoint[0], self.setpoint[1], self.setpoint[2]))

        # send the setpoint
        cf.commander.send_position_setpoint(self.setpoint[0], self.setpoint[1], self.setpoint[2], 0)


    def disconnect(self):
        """Disconnects the real drone."""
        print(self.uri, "disconnecting")
        self.isConnected = False
        cf = self.scf.cf
        cf.commander.send_stop_setpoint()
        time.sleep(0.1)
        self.scf.close_link()


    def update(self):
        """Update the virtual drone."""
        self._updateTargetForce()
        self._updateAvoidanceForce()
        self._clampForce()

        if self.isConnected:
            self.sendPosition()

        # draw various lines to get a better idea of whats happening
        self._drawTargetLine()
        # self._drawVelocityLine()
        self._drawForceLine()
        # self._drawActualDroneLine()
        # self._drawSetpointLine()

        self._printDebugInfo()


    def _updateTargetForce(self):
        """Applies a force to the virtual drone which moves it closer to its target."""
        dist = (self.target - self.getPos())
        if(dist.length() > self.FORCEFALLOFFDISTANCE):
            force = dist.normalized()
        else:
            force = (dist / self.FORCEFALLOFFDISTANCE)
        # velMult = self.getVel().length() + 0.1
        # velMult = velMult ** 2
        self.addForce(force * self.TARGETFORCE)


    def _updateAvoidanceForce(self):
        """Applies a force the the virtual drone which makes it avoid other drones."""
        # get all drones within the sensors reach and put them in a list
        others = []
        for drone in self.manager.drones:
            dist = (drone.getPos() - self.getPos()).length()
            if dist > 0 and dist < self.SENSORRANGE:  # check dist > 0 to prevent drone from detecting itself
                others.append(drone)

        # get the root mean square position of all drones involved
        # becomes just the drone position if there are no drones in sensor range
        # massVec = self.getPos() ** 2
        # for other in others:
        #     massVec += other.getPos() ** 2
        # massVec /= (others.__len__() + 1)
        # massVec = self.root(massVec)

        # calculate and apply forces
        for other in others:
            # perp = self.targetVector().cross(massVec - self.getPos())
            distVec = other.getPos() - self.getPos()
            if distVec.length() < 0.2:
                print("BONK")
            # distMult = max(0, self.SENSORRANGE - distVec.length())
            distMult = self.SENSORRANGE - distVec.length()
            # avoidanceVector = perp.normalized() * 0.1 - distVec.normalized() * 0.9
            avoidanceDirection = self.randVec.normalized() * 2 - distVec.normalized() * 10
            avoidanceDirection.normalize()
            self.addForce(avoidanceDirection * distMult * self.AVOIDANCEFORCE)


    def _clampForce(self):
        """Clamps the total force acting in the drone."""
        totalForce = self.rigidBody.getTotalForce()
        if totalForce.length() > 2:
            self.rigidBody.clearForces()
            self.rigidBody.applyCentralForce(totalForce.normalized())


    # def root(self, vec: Vec3) -> Vec3:
    #     """Takes the root of all elements of the supplied vector and returns it."""
    #     x = math.sqrt(vec.x)
    #     y = math.sqrt(vec.y)
    #     z = math.sqrt(vec.z)
    #     return Vec3(x, y, z)


    def targetVector(self) -> Vec3:
        """Returns the vector from the drone to its target."""
        return self.target - self.getPos()


    def _printDebugInfo(self):
        if self.printDebugInfo:
            pass


    def setTarget(self, target: Vec3):
        """Sets a new target for the drone."""
        self.target = target


    def setRandomTarget(self):
        """Sets a new random target for the drone."""
        self.target = self.manager.getRandomRoomCoordinate()


    def addForce(self, force: Vec3):
        self.rigidBody.applyCentralForce(force)


    def getPos(self) -> Vec3:
        return self.rigidBodyNP.getPos()


    def setPos(self, position: Vec3):
        self.rigidBodyNP.setPos(position)


    def getVel(self) -> Vec3:
        return self.rigidBody.getLinearVelocity()


    def setVel(self, velocity: Vec3):
        return self.rigidBody.setLinearVelocity(velocity)


    def _drawTargetLine(self):
        self.targetLineNP.removeNode()
        ls = LineSegs()
        # ls.setThickness(1)
        ls.setColor(1.0, 0.0, 0.0, 1.0)
        ls.moveTo(self.getPos())
        ls.drawTo(self.target)
        node = ls.create()
        self.targetLineNP = self.base.render.attachNewNode(node)


    def _drawVelocityLine(self):
        self.velocityLineNP.removeNode()
        ls = LineSegs()
        # ls.setThickness(1)
        ls.setColor(0.0, 0.0, 1.0, 1.0)
        ls.moveTo(self.getPos())
        ls.drawTo(self.getPos() + self.getVel())
        node = ls.create()
        self.velocityLineNP = self.base.render.attachNewNode(node)


    def _drawForceLine(self):
        self.forceLineNP.removeNode()
        ls = LineSegs()
        # ls.setThickness(1)
        ls.setColor(0.0, 1.0, 0.0, 1.0)
        ls.moveTo(self.getPos())
        ls.drawTo(self.getPos() + self.rigidBody.getTotalForce() * 0.2)
        node = ls.create()
        self.forceLineNP = self.base.render.attachNewNode(node)


    def _drawActualDroneLine(self):
        self.actualDroneLineNP.removeNode()
        ls = LineSegs()
        # ls.setThickness(1)
        ls.setColor(0.0, 0.0, 0.0, 1.0)
        ls.moveTo(self.getPos())
        ls.drawTo(self.actualDronePosition)
        node = ls.create()
        self.actualDroneLineNP = self.base.render.attachNewNode(node)


    def _drawSetpointLine(self):
        self.setpointNP.removeNode()
        ls = LineSegs()
        # ls.setThickness(1)
        ls.setColor(1.0, 1.0, 1.0, 1.0)
        ls.moveTo(self.getPos())
        ls.drawTo(self.setpoint)
        node = ls.create()
        self.setpointNP = self.base.render.attachNewNode(node)


    def _wait_for_position_estimator(self):
        """Waits until the position estimator reports a consistent location after resetting."""
        print('Waiting for estimator to find position...')

        log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
        log_config.add_variable('kalman.varPX', 'float')
        log_config.add_variable('kalman.varPY', 'float')
        log_config.add_variable('kalman.varPZ', 'float')

        var_y_history = [1000] * 10
        var_x_history = [1000] * 10
        var_z_history = [1000] * 10

        threshold = 0.001

        with SyncLogger(self.scf, log_config) as logger:
            for log_entry in logger:
                data = log_entry[1]

                var_x_history.append(data['kalman.varPX'])
                var_x_history.pop(0)
                var_y_history.append(data['kalman.varPY'])
                var_y_history.pop(0)
                var_z_history.append(data['kalman.varPZ'])
                var_z_history.pop(0)

                min_x = min(var_x_history)
                max_x = max(var_x_history)
                min_y = min(var_y_history)
                max_y = max(var_y_history)
                min_z = min(var_z_history)
                max_z = max(var_z_history)

                if (max_x - min_x) < threshold and (
                        max_y - min_y) < threshold and (
                        max_z - min_z) < threshold:
                    break


    def _reset_estimator(self):
        """Resets the position estimator, this should be run before flying the drones or they might report a wrong position."""
        cf = self.scf.cf
        cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        cf.param.set_value('kalman.resetEstimation', '0')

        self._wait_for_position_estimator()


    def position_callback(self, timestamp, data, logconf):
        """Updates the variable holding the position of the actual drone. It is not called in the update method, but by the drone itself (I think)."""
        x = data['kalman.stateX']
        y = data['kalman.stateY']
        z = data['kalman.stateZ']
        self.realDronePosition = Vec3(x, y, z)
        # print('pos: ({}, {}, {})'.format(x, y, z))


    def start_position_printing(self):
        """Activate logging of the position of the real drone."""
        log_conf = LogConfig(name='Position', period_in_ms=50)
        log_conf.add_variable('kalman.stateX', 'float')
        log_conf.add_variable('kalman.stateY', 'float')
        log_conf.add_variable('kalman.stateZ', 'float')

        self.scf.cf.log.add_config(log_conf)
        log_conf.data_received_cb.add_callback(self.position_callback)
        log_conf.start()
