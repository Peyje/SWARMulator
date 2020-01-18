# This simulation is influenced by the original sim of Florian Swienty.

# Load  Panda3D modules
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties
from panda3d.core import Vec3
from panda3d.core import AntialiasAttrib
from panda3d.core import DirectionalLight
from panda3d.core import NativeWindowHandle
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

# Load classes from other files
from camera_control import CameraControl

# Import needed modules
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib


class Handler:
    """
    Handles all input into the GUI, such as button presses.

    All on[..] functions are invoked by the GUI itself.
    """
    # Stored to later control the camera through keypresses
    cam_control = []

    # Stored to later control the visibility switching of the bullet debug mode
    bullet_debug_node = []

    def __init__(self):
        self.test_1_button = builder.get_object("test1Button")
        self.test_2_button = builder.get_object("test2Button")

    def onTest1Press(self, button):
        """
        Print that button has been pressed.
        """
        print("Test Button 1 pressed")

    def onTest2Press(self, button):
        """
        Print that button has been pressed.
        """
        print("Test Button 2 pressed")

    def onKeyPress(self, area, event):
        """
        Called on any key press, it finds the corresponding function and calls it. Mostly used for moving the camera.
        """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname == 'w':
            Handler.cam_control.update_forward_trig(1)
        if keyname == 's':
            Handler.cam_control.update_forward_trig(-1)
        if keyname == 'a':
            Handler.cam_control.update_right_trig(-1)
        if keyname == 'd':
            Handler.cam_control.update_right_trig(1)
        if keyname == 'Shift_L':
            Handler.cam_control.update_up_trig(1)
        if keyname == 'Control_L':
            Handler.cam_control.update_up_trig(-1)
        if keyname == 'q':
            Handler.cam_control.update_heading_trig(1)
        if keyname == 'e':
            Handler.cam_control.update_heading_trig(-1)
        if keyname == 'r':
            Handler.cam_control.update_pitch_trig(1)
        if keyname == 'f':
            Handler.cam_control.update_pitch_trig(-1)

        if keyname == 'F1':
            if Handler.bullet_debug_node.isHidden():
                Handler.bullet_debug_node.show()
            else:
                Handler.bullet_debug_node.hide()


    def onKeyRelease(self, area, event):
        """
        Same as onKeyPress, but called on the release of a key press.
        """
        keyname = Gdk.keyval_name(event.keyval)

        if keyname == 'w' or keyname == 's':
            Handler.cam_control.update_forward_trig(0)
        if keyname == 'a' or keyname == 'd':
            Handler.cam_control.update_right_trig(0)
        if keyname == 'Shift_L' or keyname == 'Control_L':
            Handler.cam_control.update_up_trig(0)
        if keyname == 'q' or keyname == 'e':
            Handler.cam_control.update_heading_trig(0)
        if keyname == 'r' or keyname == 'f':
            Handler.cam_control.update_pitch_trig(0)


class Simulator(ShowBase):
    """
    Main class of the simulation itself. Mostly initialisation.
    """

    def __init__(self):
        """
        Creates the window, loads the scene and models and sets everything up.
        """
        # Initialise panda window
        ShowBase.__init__(self)
        self.setBackgroundColor(.1, .1, .1)

        # Setup window
        wp = WindowProperties()
        wp.setOrigin(0, 0)
        wp.setSize(1024, 768)

        # Get drawing area and set its size
        panda_drawing_area = builder.get_object("pandaDrawingArea")
        panda_drawing_area.set_size_request(1024, 768)

        # Panda should not open own top level window but use the window of the drawing area in GTK
        handle = NativeWindowHandle.makeInt(panda_drawing_area.get_property('window').get_xid())
        wp.setParentWindow(handle)

        # Open panda window
        self.openDefaultWindow(props=wp)

        def gtk_iteration(task):
            """
            Handles the gtk events and lets as many GUI iterations run as needed.
            """
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
            return task.cont

        # Create task to update GUI
        self.taskMgr.add(gtk_iteration, "gtk")

        # Activate antialiasing (MAuto for automatic selection of AA form)
        self.render.setAntialias(AntialiasAttrib.MAuto)

        # Deactivate default mouse control of the camera as they are not very helpful
        self.disableMouse()

        # Set camera to default position and orientation
        self.camera.setPos(-4, 0, 2)
        self.camera.lookAt(0, 0, 1)
        self.camLens.setFov(90)

        # Load the camera control events to control camera by keyboard
        self.cam_control = CameraControl(self)
        # Store it as a class variable of the Handler so the controller can be called by it
        Handler.cam_control = self.cam_control

        # Load scene
        # TODO: Design a new room
        self.scene = self.loader.loadModel("models/rooms/room_neu.egg")
        self.scene.reparentTo(self.render)  # Panda3D makes use of a scene graph, where "render" is the parent of the
        # tree containing all objects to be rendered

        # Add lights
        # TODO: Make the lighting somewhat nicer (maybe with some ambient lights?)
        for i in range(0, 3):
            dlight = DirectionalLight("light")
            dlnp = self.render.attachNewNode(dlight)
            dlnp.setHpr((120 * i) + 1, -30, 0)
            self.render.setLight(dlnp)

        # Create a bullet world (physics engine)
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        def update_bullet(task):
            """
            Invokes the physics engine to update and simulate the next step.
            """
            dt = globalClock.getDt()  # get elapsed time
            self.world.doPhysics(dt)  # actually update
            return task.cont

        # Create task to update physics
        self.taskMgr.add(update_bullet, 'update_bullet')

        # Set up the ground for the physics engine
        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)  # create a collision shape
        ground_node_bullet = BulletRigidBodyNode('Ground')  # create rigid body
        ground_node_bullet.addShape(ground_shape)  # add shape to it

        ground_node_panda = self.render.attachNewNode(ground_node_bullet)  # attach to panda scene graph
        ground_node_panda.setPos(0, 0, 0)  # set position

        self.world.attachRigidBody(ground_node_bullet)  # attach to physics world

        # Create and activate a debug node for bullet and attach it to the panda scene graph
        debug_node_bullet = BulletDebugNode('Debug')
        debug_node_bullet.showWireframe(True)
        debug_node_bullet.showConstraints(True)
        debug_node_bullet.showBoundingBoxes(True)
        debug_node_bullet.showNormals(True)
        debug_node_panda = self.render.attachNewNode(debug_node_bullet)
        # debug_node_panda.show()
        self.world.setDebugNode(debug_node_panda.node())

        # Store it as a class variable of the Handler so the debug mode can be switched by it
        Handler.bullet_debug_node = debug_node_panda


if __name__ == "__main__":
    # Load the GTK builder for the GUI
    builder = Gtk.Builder()

    # Load GTK GUI
    builder.add_from_file("layout.glade")

    # Connect GUI to program
    builder.connect_signals(Handler())

    # Function to call when program is supposed to quit
    def close_app(*args, **kw):
        # Gtk.main_quit()  # actually not needed as no main loop is running (gtk_main_iteration_do is used)
        sys.exit(0)

    # Main GUI code
    window = builder.get_object("main")
    window.connect("destroy", close_app)
    window.show_all()

    # Start the simulation
    app = Simulator()
    app.run()

