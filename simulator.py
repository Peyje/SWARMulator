# This simulation is influenced by the original sim of Florian Swienty.

# Import needed modules
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

# Load  Panda3D modules
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from panda3d.core import AntialiasAttrib
from panda3d.core import DirectionalLight
from panda3d.core import NativeWindowHandle
from direct.task import Task

# Load classes from other files
from camera_control import CameraControl


def gtk_iteration(*args, **kw):
    """
    Handles the gtk events and lets as many GUI iterations run as needed.
    """
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)
    return Task.cont


class Handler:
    """
    Handles all input into the GUI, such as button presses.

    All on[..] functions are invoked by the GUI itself.
    """
    # Stored to later control the camera through keypresses
    cam_control = []

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

        # Create task to update GUI
        self.taskMgr.add(gtk_iteration, "gtk")


if __name__ == "__main__":
    # Load the GTK builder for the GUI
    builder = Gtk.Builder()

    # Load GTK GUI
    builder.add_from_file("layout.glade")

    # Connect GUI to program
    builder.connect_signals(Handler())

    # Function to call when program is supposed to quit
    def close_app(*args, **kw):
        Gtk.main_quit()
        sys.exit(0)

    # Main GUI code
    window = builder.get_object("main")
    window.connect("destroy", close_app)
    window.show_all()

    # Start the simulation
    app = Simulator()
    app.run()

