# This simulation is influenced by the original sim of Florian Swienty.

# Load  Panda3D modules
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import WindowProperties
from panda3d.core import LVector3f
from panda3d.core import AntialiasAttrib
from panda3d.core import DirectionalLight
from panda3d.core import NativeWindowHandle
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletRigidBodyNode, BulletDebugNode

# Load classes from other files
from handler import Handler
from camera_control import CameraControl
from drone_manager import DroneManager

# Import needed modules
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


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
		self.camera.setPos(0, -4, 2)
		self.camera.lookAt(0, 0, 1)
		self.camLens.setFov(90)

		# Load the camera control events to control camera by keyboard
		self.cam_control = CameraControl(self)
		# Store it as a class variable of the Handler so the controller can be called by it
		Handler.cam_control = self.cam_control

		# Load scene
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
		# self.world.setGravity(LVector3f(0, 0, -9.81))
		self.world.setGravity(LVector3f(0, 0, 0))  # No gravity for now (makes forces easier to calculate)

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
		ground_shape = BulletPlaneShape(LVector3f(0, 0, 1), 0)  # create a collision shape
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

		# Load the class to manage the drones
		self.drone_manager = DroneManager(self)
		# Store it as a class variable of the Handler changes can be invoked
		Handler.drone_manager = self.drone_manager


if __name__ == "__main__":
	# Load the GTK builder for the GUI
	builder = Gtk.Builder()

	# Load GTK GUI
	builder.add_from_file("layout.glade")

	# Load some custom CSS
	css_provider = Gtk.CssProvider()
	css_provider.load_from_path("gui.css")
	Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

	# Connect GUI to program
	builder.connect_signals(Handler(builder))

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

