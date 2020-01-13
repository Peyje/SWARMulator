from direct.showbase import DirectObject
from panda3d.core import KeyboardButton
from panda3d.core import WindowProperties
from panda3d.core import Vec3


class CameraController(DirectObject.DirectObject):

    def __init__(self, base):
        self.base = base
        self.base.disableMouse()

        self.camera = base.camera
        self.cameraControlActive = False
        self.camera.setPos(-5, 0, 2)
        self.camera.lookAt(0, 0, 1)
        base.camLens.setFov(90)
        base.camLens.setNear(.1)

        self.anchorX = 0
        self.anchorY = 0
        self.setAnchor = True

        self.accept("mouse3", self.activateCameraControl)
        self.accept("mouse3-up", self.deactivateCameraControl)


    def activateCameraControl(self):
        props = WindowProperties()
        self.cameraControlActive = True
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)
        windowSizeX = self.base.win.getProperties().getXSize()
        windowSizeY = self.base.win.getProperties().getYSize()
        self.setAnchor = True
        self.base.taskMgr.add(self.cameraControlTask, "CameraControlTask", extraArgs=[windowSizeX, windowSizeY], appendTask=True)


    def deactivateCameraControl(self):
        props = WindowProperties()
        self.cameraControlActive = False
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)
        self.base.taskMgr.remove("CameraControlTask")



    def cameraControlTask(self, windowSizeX, windowSizeY, task):

        mw = self.base.mouseWatcherNode
        curPos = self.camera.getPos()
        curHpr = self.camera.getHpr()
        forward = self.camera.getQuat().getForward()
        right = self.camera.getQuat().getRight()
        up = self.camera.getQuat().getUp()
        moveSpeed = .05
        rotSpeed = 20

        # get initial mouse position, this runs only once on the first frame after the task is added to the taskmanager
        if self.setAnchor:
            self.anchorX = mw.getMouseX()
            self.anchorY = mw.getMouseY()
            self.setAnchor = False

        # update rotation
        if mw.hasMouse():
            deltaX = rotSpeed * ((mw.getMouseX() - self.anchorX))
            deltaY = rotSpeed * ((mw.getMouseY() - self.anchorY))
            self.base.win.movePointer(0, int((0.5 * self.anchorX + 0.5) * windowSizeX), int((-0.5 * self.anchorY + 0.5) * windowSizeY))

            threshold = 0.05
            if abs(deltaX) < threshold:
                deltaX = 0
            if abs(deltaY) < threshold:
                deltaY = 0

            self.camera.setHpr(curHpr.getX() - deltaX, curHpr.getY() + deltaY, 0)

        # update position
        deltaPos = Vec3(0, 0, 0)
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('w', 'utf-8'))):
            deltaPos += forward
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('s', 'utf-8'))):
            deltaPos -= forward
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('d', 'utf-8'))):
            deltaPos += right
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('a', 'utf-8'))):
            deltaPos -= right
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('e', 'utf-8'))):
            deltaPos += up
        if mw.isButtonDown(KeyboardButton.asciiKey(bytes('q', 'utf-8'))):
            deltaPos -= up
        deltaPos.normalize()
        deltaPos *= moveSpeed
        self.camera.setPos(curPos + deltaPos)

        return task.cont
