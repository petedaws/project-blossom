import numpy
import time
import sys
import entityset1
import entity_generator
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

G = 98000
dt = 0.0001
screensize = (1024,768)
zoom = -500.0
xpos = 0
scale = 10.0
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
		self.id = id
		self.position = position 
		self.velocity = velocity
		self.acceleration = acceleration
		self.mass = mass
		self.color = color

	def distance_to_entity(self,ent):
		r = ent.position - self.position
		return numpy.linalg.norm(r)

	def calc_gravity(self,entities):
		self.acceleration = numpy.array([0.0,0.0,0.0])
		for ent in entities:
			if ent.id == self.id:
				continue
			rabs = self.distance_to_entity(ent)
			g_abs = G*ent.mass*1/(rabs**2)
			g = g_abs*(ent.position - self.position)/rabs
			self.acceleration = self.acceleration + g
			

	def propogate_linear(self,dt):
		self.velocity = self.velocity + dt*self.acceleration
		self.position = self.position + dt*self.velocity
		
	def draw(self):
		glLoadIdentity()
		glTranslatef(self.position[0],self.position[1],self.position[2])		# Move Right And Into The Screen
		glScaled(scale,scale,scale)
		glColor3f(*self.color)			# Set The Color To Blue
		glutWireSphere(1.0,10,10)
		# glBegin(GL_QUADS)			# Start Drawing The Cube


		# glColor3f(0.0,1.0,0.0)			# Set The Color To Blue
		# glVertex3f( 1.0, 1.0,-1.0)		# Top Right Of The Quad (Top)
		# glVertex3f(-1.0, 1.0,-1.0)		# Top Left Of The Quad (Top)
		# glVertex3f(-1.0, 1.0, 1.0)		# Bottom Left Of The Quad (Top)
		# glVertex3f( 1.0, 1.0, 1.0)		# Bottom Right Of The Quad (Top)

		# glColor3f(1.0,0.5,0.0)			# Set The Color To Orange
		# glVertex3f( 1.0,-1.0, 1.0)		# Top Right Of The Quad (Bottom)
		# glVertex3f(-1.0,-1.0, 1.0)		# Top Left Of The Quad (Bottom)
		# glVertex3f(-1.0,-1.0,-1.0)		# Bottom Left Of The Quad (Bottom)
		# glVertex3f( 1.0,-1.0,-1.0)		# Bottom Right Of The Quad (Bottom)

		# glColor3f(1.0,0.0,0.0)			# Set The Color To Red
		# glVertex3f( 1.0, 1.0, 1.0)		# Top Right Of The Quad (Front)
		# glVertex3f(-1.0, 1.0, 1.0)		# Top Left Of The Quad (Front)
		# glVertex3f(-1.0,-1.0, 1.0)		# Bottom Left Of The Quad (Front)
		# glVertex3f( 1.0,-1.0, 1.0)		# Bottom Right Of The Quad (Front)

		# glColor3f(1.0,1.0,0.0)			# Set The Color To Yellow
		# glVertex3f( 1.0,-1.0,-1.0)		# Bottom Left Of The Quad (Back)
		# glVertex3f(-1.0,-1.0,-1.0)		# Bottom Right Of The Quad (Back)
		# glVertex3f(-1.0, 1.0,-1.0)		# Top Right Of The Quad (Back)
		# glVertex3f( 1.0, 1.0,-1.0)		# Top Left Of The Quad (Back)

		# glColor3f(0.0,0.0,1.0)			# Set The Color To Blue
		# glVertex3f(-1.0, 1.0, 1.0)		# Top Right Of The Quad (Left)
		# glVertex3f(-1.0, 1.0,-1.0)		# Top Left Of The Quad (Left)
		# glVertex3f(-1.0,-1.0,-1.0)		# Bottom Left Of The Quad (Left)
		# glVertex3f(-1.0,-1.0, 1.0)		# Bottom Right Of The Quad (Left)

		# glColor3f(1.0,0.0,1.0)			# Set The Color To Violet
		# glVertex3f( 1.0, 1.0,-1.0)		# Top Right Of The Quad (Right)
		# glVertex3f( 1.0, 1.0, 1.0)		# Top Left Of The Quad (Right)
		# glVertex3f( 1.0,-1.0, 1.0)		# Bottom Left Of The Quad (Right)
		# glVertex3f( 1.0,-1.0,-1.0)		# Bottom Right Of The Quad (Right)
		# glEnd()				# Done Drawing The Quad
		
entities = []

sun = {'id':'sun',
  'position':numpy.array([0.0,0.0,0.0]),
  'velocity':numpy.array([0.0,0.0,0.0]),
  'acceleration':numpy.array([0.0,0.0,0.0]),
  'mass':50000.0,
  'color':[1.0,1.0,0.0]}

entities.append(entity(**sun))

for e in entity_generator.generate(count=30,gravity_enabled=True):
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
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100000000000000000.0)
	gluLookAt(0.0,0.0,zoom,0.0,0.0,0.0,0.0,1.0,0.0)
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
	gluLookAt(0.0,0.0,zoom,0.0,0.0,0.0,0.0,1.0,0.0)
	glMatrixMode(GL_MODELVIEW)


# The main drawing function. 
def DrawGLScene():
	glMatrixMode(GL_MODELVIEW)
	glViewport(0, 0, screensize[0], screensize[1]) 	# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(screensize[0])/float(screensize[1]), 0.1, 100000000000000000.0)
	gluLookAt(xpos,0.0,zoom,xpos,0.0,0.0,0.0,1.0,0.0)
	glMatrixMode(GL_MODELVIEW)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()					# Reset The View
	for ent in entities:
		ent.calc_gravity(entities)
		ent.propogate_linear(dt)
		ent.draw()
	glutSwapBuffers()

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)	
def keyPressed(*args):
	global zoom
	global scale
	global xpos
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()
	
	if args[0] == 'w':
		zoom = zoom + 50
		#scale = numpy.abs(zoom)
		
	if args[0] == 's':
		zoom = zoom - 50
		#scale = numpy.abs(zoom)
		
	if args[0] == 'a':
		xpos = xpos + 10
		
	if args[0] == 'd':
		xpos = xpos - 10
		#scale = numpy.abs(zoom)


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

