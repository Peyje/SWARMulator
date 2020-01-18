# Load further needed Panda3D modules
from direct.gui.DirectGui import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.showbase import DirectObject
from panda3d.core import Vec3


def reset_camera(base):
	"""
	Set camera to default position.
	"""
	base.camera.setPos(-4, 0, 2)
	base.camera.lookAt(0, 0, 1)


class CameraControl(DirectObject.DirectObject):
	"""
	This class takes care of the commands to the camera, e.g. event handling, setting up the update task and more.
	The accept-calls are only working if panda has its own top level window and key presses are propagated to it.
	"""

	def __init__(self, base):
		"""
		Set up trigger, get movement directions and create event handling.
		"""
		super().__init__()

		# Trigger to tell where the camera is supposed to go
		self.forward_trig = 0
		self.right_trig = 0
		self.up_trig = 0
		self.heading_trig = 0
		self.pitch_trig = 0

		# Store the movement needed to go in each direction (updated in task)
		self.forward = 0
		self.right = 0
		self.up = 0

		# Event handling for key down events
		self.accept('w', self.set_forward_trig, [1])
		self.accept('s', self.set_forward_trig, [-1])
		self.accept('a', self.set_right_trig, [-1])
		self.accept('d', self.set_right_trig, [1])
		self.accept('shift', self.set_up_trig, [1])
		self.accept('control', self.set_up_trig, [-1])
		self.accept('q', self.set_heading_trig, [1])
		self.accept('e', self.set_heading_trig, [-1])
		self.accept('r', self.set_pitch_trig, [1])
		self.accept('f', self.set_pitch_trig, [-1])

		# Event handling for key up events
		self.accept('w-up', self.set_forward_trig, [0])
		self.accept('s-up', self.set_forward_trig, [0])
		self.accept('a-up', self.set_right_trig, [0])
		self.accept('d-up', self.set_right_trig, [0])
		self.accept('shift-up', self.set_up_trig, [0])
		self.accept('control-up', self.set_up_trig, [0])
		self.accept('q-up', self.set_heading_trig, [0])
		self.accept('e-up', self.set_heading_trig, [0])
		self.accept('r-up', self.set_pitch_trig, [0])
		self.accept('f-up', self.set_pitch_trig, [0])

		# Start task to move camera in desired direction
		base.taskMgr.add(self.cam_move_task, "CamMoveTask", extraArgs=[base], appendTask=True)

		# Create button to reset camera position and orientation
		frame = DirectFrame(frameColor=(.1, .1, .1, .7), frameSize=(-.22, .22, -.05, .08), pos=(-1.1, 0, -0.94))
		button = DirectButton(text="Reset Camera", frameSize=(-4, 4, -.5, 1), scale=.05, command=reset_camera, extraArgs=[base])
		button.reparentTo(frame)

	def set_forward_trig(self, trig):
		"""
		Event handling function for for/backward movement command.
		"""
		self.forward_trig = trig

	def set_right_trig(self, trig):
		"""
		Event handling function for left/right movement command.
		"""
		self.right_trig = trig

	def set_up_trig(self, trig):
		"""
		Event handling function for up/downward movement command.
		"""
		self.up_trig = trig

	def set_heading_trig(self, trig):
		"""
		Event handling function for heading rotation command.
		"""
		self.heading_trig = trig

	def set_pitch_trig(self, trig):
		"""
		Event handling function for pitch rotation command.
		"""
		self.pitch_trig = trig

	def cam_move_task(self, base, task):
		"""
		Task function for actually updating the position of the camera.
		"""
		# Get current position, reset delta
		cur_pos = base.camera.getPos()
		cur_hpr = base.camera.getHpr()
		delta_pos = Vec3(0, 0, 0)

		# Update the movement needed to go in each direction (rotation changes these)
		self.forward = base.camera.getQuat().getForward()
		self.right = base.camera.getQuat().getRight()
		self.up = base.camera.getQuat().getUp()

		# Check if movement is wanted
		if self.forward_trig == 1:
			delta_pos += self.forward
		elif self.forward_trig == -1:
			delta_pos -= self.forward
		if self.right_trig == 1:
			delta_pos += self.right
		elif self.right_trig == -1:
			delta_pos -= self.right
		if self.up_trig == 1:
			delta_pos += self.up
		elif self.up_trig == -1:
			delta_pos -= self.up

		# Fine tune delta and move camera
		delta_pos.normalize()
		delta_pos *= .05
		base.camera.setPos(cur_pos + delta_pos)

		# Rotate camera as wanted
		delta_heading = self.heading_trig
		delta_pitch = self.pitch_trig
		base.camera.setHpr(cur_hpr.getX() + delta_heading, cur_hpr.getY() + delta_pitch, 0)

		# As its a task, continue with next iteration
		return task.cont
