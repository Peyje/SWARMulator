# This simulation is heavily influenced by the original sim of Florian Swienty.
# (Read: I took his already functioning sim and refactored it.)

# Load basic Panda3D modules
from direct.showbase.ShowBase import ShowBase

# Load further needed Panda3D modules, classes and containers
from panda3d.core import WindowProperties
from panda3d.core import AntialiasAttrib
from panda3d.core import DirectionalLight

# Load classes from other files
from camera_controller import CameraController
from gui import Gui


class Simulator(ShowBase):
    """
    Main class of the simulation itself. Mostly initialisation.
    """

    def __init__(self):
        """
        Creates the window, loads the scene and models and sets everything up.
        """
        # Initialise window
        ShowBase.__init__(self)
        self.setBackgroundColor(.1, .1, .1)

        # Resize region where sim is displayed
        self.cam.node().getDisplayRegion(0).setDimensions(0, 0.8, 0, 1)

        # Setup window
        wp = WindowProperties()
        wp.setSize(1024, 768)
        self.win.requestProperties(wp)

        # self.setFrameRateMeter(True)

        # Activate antialiasing (MAuto for automatic selection of AA form)
        self.render.setAntialias(AntialiasAttrib.MAuto)

        # TODO: Remake the camera controller
        CameraController(self)

        # Load scene
        self.init_scene()

        # Load GUI
        Gui(self)

    def init_scene(self):
        """
        Load room model and set up some lights (how romantic..).
        """
        # TODO: Design a new room
        self.scene = self.loader.loadModel("models/rooms/room_florian.egg")
        self.scene.reparentTo(self.render)  # Panda3D makes use of a scene graph, where "render" is the parent of the
        # tree containing all objects to be rendered

        # Add lights
        # TODO: Make the lighting somewhat nicer (maybe with some ambient lights?)
        for i in range(0, 3):
            dlight = DirectionalLight("light")
            dlnp = self.render.attachNewNode(dlight)
            dlnp.setHpr((120 * i) + 1, -30, 0)
            self.render.setLight(dlnp)

        # TODO: Rest of the simulator


if __name__ == "__main__":
    # Start the simulation
    app = Simulator()
    app.run()

