# Load further needed Panda3D modules, classes and containers
from panda3d.core import Camera
from panda3d.core import PGTop
from panda3d.core import NodePath
from panda3d.core import OrthographicLens
from panda3d.core import MouseWatcher

# Load GUI elements
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectGui import DirectButton


class Gui:
	"""
	The main class of the GUI which is set to the right of the sim region.
	"""

	def __init__(self, base):
		"""
		Creates a new display region to the right and sets up a new render parent for the 2D GUI.
		"""

		# As the original render is working on the simulation, this render is parent for GUI elements
		render_gui = NodePath('renderGui')
		# Only 2D, no depth needed
		render_gui.setDepthTest(False)
		render_gui.setDepthWrite(False)

		# Create a new display region for the GUI and let render last
		region_gui = base.win.makeDisplayRegion(0.8, 1, 0, 1)
		region_gui.setSort(20)

		# Create a new camera for the region to show the buttons
		cam_gui = NodePath(Camera('camGui'))
		lens = OrthographicLens()
		lens.setFilmSize(2, 2)
		lens.setNearFar(-1000, 1000)
		cam_gui.node().setLens(lens)
		cam_gui.reparentTo(render_gui)

		region_gui.setCamera(cam_gui)

		# All interactive objects have to be connected to a PGTop node, which we create here as a aspect ratio,
		# based on the original aspect2d of the base view
		aspect_ratio = base.getAspectRatio()
		aspect2d_gui = render_gui.attachNewNode(PGTop('myAspect2d'))
		# aspect2d_gui.setScale(1.0 / aspect_ratio, 1.0, 1.0)
		aspect2d_gui.setScale(1.0, 1.0, 1.0)

		# Create a new mouse watcher for the gui region
		mouse_watcher_gui = MouseWatcher()
		base.mouseWatcher.getParent().attachNewNode(mouse_watcher_gui)
		mouse_watcher_gui.setDisplayRegion(region_gui)
		aspect2d_gui.node().setMouseWatcher(mouse_watcher_gui)

		# Create frame that is parent of all GUI elements
		main_frame_gui = DirectFrame(frameColor=(.2, .2, .2, 1), frameSize=(-1, 1, -1, 1), pos=(0, 0, 0))
		main_frame_gui.reparentTo(aspect2d_gui)

		# Test Button
		buttonSize = (-4, 4, -.2, .8)
		button = DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.1, frameSize=buttonSize, command=self.test)
		button["extraArgs"] = [button]
		button.reparentTo(main_frame_gui)

	def test(self, button):
		print("hi")
