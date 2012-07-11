import numpy
import time
import sys
import entityset1
import entity_generator
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from itertools import tee, izip


G = 98000
dt = 0.0001
screensize = (1024,768)
zoom = -500.0
camera_z = 1.0
camera_x = 0.0
xpos = 0
view_angle = 0.0
scale = 5.0
display_history = True
history_size = 150
entity_count = 30
# ascii codes for various special keys
ESCAPE = 27
PAGE_UP = 73
PAGE_DOWN = 81
UP_ARROW = 72
DOWN_ARROW = 80
LEFT_ARROW = 75
RIGHT_ARROW = 77

class entity():
	def __init__(self,id,position,velocity,acceleration,mass,color):
		global history_size
		self.id = id
		self.position = position 
		self.velocity = velocity
		self.acceleration = acceleration
		self.mass = mass
		self.color = color
		self.position_history = self.data = [None for i in xrange(history_size)]

	def calc_gravity(self,entities):
		self.acceleration = numpy.array([0.0,0.0,0.0])
		for ent in entities:
			if ent.id == self.id:
				continue
			rabs = numpy.linalg.norm(ent.position - self.position)
			g_abs = G*ent.mass*1/(rabs**2)
			g = g_abs*(ent.position - self.position)/rabs
			self.acceleration = self.acceleration + g
			

	def propogate_linear(self,dt):
		self.velocity = self.velocity + dt*self.acceleration
		self.position = self.position + dt*self.velocity
		self.position_history.pop(0)
		self.position_history.append(self.position)
		
	def draw(self):
		def pairwise(iterable):
			"s -> (s0,s1), (s1,s2), (s2, s3), ..."
			a, b = tee(iterable)
			next(b, None)
			return izip(a, b)
		glPushMatrix()
		glTranslatef(self.position[0],self.position[1],self.position[2])		# Move Right And Into The Screen
		mass_scale = scale+self.mass*0.0001
		glScaled(mass_scale,mass_scale,mass_scale)
		glColor3f(*self.color)			# Set The Color To Blue
		glutWireSphere(1.0,10,10)
		glPopMatrix()
		glPushMatrix()
		if display_history:
			for pos, pos_next in pairwise(self.position_history):
				if pos is not None and pos_next is not None:
					glBegin(GL_LINES)
					glVertex3f(pos[0],
							   pos[1],
							   pos[2])
					glVertex3f(pos_next[0],
							   pos_next[1],
							   pos_next[2])
					glEnd()
		glPopMatrix()
	
entities = []

sun = {'id':'sun2',
  'position':numpy.array([1000.0,0.0,0.0]),
  'velocity':numpy.array([0.0,2000.0,0.0]),
  'acceleration':numpy.array([0.0,0.0,0.0]),
  'mass':100000.0,
  'color':[1.0,1.0,0.0]}
  
sun = {'id':'sun',
  'position':numpy.array([0.0,0.0,0.0]),
  'velocity':numpy.array([0.0,0.0,0.0]),
  'acceleration':numpy.array([0.0,0.0,0.0]),
  'mass':100000.0,
  'color':[1.0,1.0,0.0]}

entities.append(entity(**sun))
#entities.append(entity(**sun2))

for e in entity_generator.generate(count=entity_count,gravity_enabled=False):
	entities.append(entity(**e))


# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
	glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
	glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
	glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
	glEnable(GL_DEPTH_TEST) 			# Enables Depth Testing
	glShadeModel(GL_SMOOTH) 			# Enables Smooth Color Shading
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()					# Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window

	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100000000000000000.0)
	glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
	if Height == 0: 					# Prevent A Divide By Zero If The Window Is Too Small 
		Height = 1
	glMatrixMode(GL_MODELVIEW)
	glViewport(0, 0, Width, Height) 	# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100000000000000000.0)
	glMatrixMode(GL_MODELVIEW)


# The main drawing function. 
def DrawGLScene():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(camera_x,0.0,camera_z,xpos,0.0,0.0,0.0,1.0,0.0)	
	glPushMatrix()
	for ent in entities:
		ent.calc_gravity(entities)
		ent.propogate_linear(dt)
		ent.draw()
	glPopMatrix()

	glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)	
def keyPressed(*args):
	global zoom
	global camera_z
	global camera_x
	global scale
	global xpos
	global view_angle
	global display_history
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()
	
	if args[0] == 'w':
		zoom = zoom + 50
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		#scale = numpy.abs(zoom)
		
	if args[0] == 's':
		zoom = zoom - 50
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		#scale = numpy.abs(zoom)
		
	if args[0] == 'a':
		#xpos = xpos + 10
		view_angle = view_angle + 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'd':
		#xpos = xpos - 10
		#scale = numpy.abs(zoom)
		view_angle = view_angle - 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'h':
		if display_history:
			display_history = False
		else:
			display_history = True
		
	


def mouse(button, state, x, y):
	global zoom
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
		zoom = zoom + 50
	elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
		zoom = zoom - 50
		
def main():
	global window

	# pass arguments to init
	glutInit(sys.argv)

	# Select type of Display mode:	 
	#  Double buffer 
	#  RGBA color
	# Alpha components supported 
	# Depth buffer
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	
	# get a 640 x 480 window 
	glutInitWindowSize(screensize[0], screensize[1])
	
	# the window starts at the upper left corner of the screen 
	glutInitWindowPosition(0, 0)
	
	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python (like myself), remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")

	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc(DrawGLScene)
	
	# Uncomment this line to get full screen.
	#glutFullScreen()

	# When we are doing nothing, redraw the scene.
	glutIdleFunc(DrawGLScene)
	
	# Register the function called when our window is resized.
	glutReshapeFunc(ReSizeGLScene)
	
	glutMouseFunc(mouse)
	
	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)

	# Initialize our window. 
	InitGL(screensize[0], screensize[1])
	
	# Start Event Processing Engine 
	glutMainLoop()
		
		
if __name__ == "__main__":
	main()

