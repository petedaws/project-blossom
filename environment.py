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
dt = 0.1
screensize = (1024,768)
zoom = -500.0
camera_z = 1.0
camera_x = 0.0
xpos = 0
view_angle = 0.0
scale = 5.0
display_history = True
display_kinetic = True
display_acceleration = True
paused = True
history_size = 15
entity_count = 0
merge_threshold = 10
max_accel = 100000
# ascii codes for various special keys
ESCAPE = 27
PAGE_UP = 73
PAGE_DOWN = 81
UP_ARROW = 72
DOWN_ARROW = 80
LEFT_ARROW = 75
RIGHT_ARROW = 77
kv = [0,0,0,0]
kr = [0,0,0,0]

def orbit_generate(ent,count=10,gravity_enabled=False):
	entities = []
	pos_low = -500.0
	pos_high = 500.0
	vel_high = 1.0
	vel_low = 0.7
	mass_high = 1.0
	mass_low = 1.0
	vel_factor = 98000.0 * 100000.0
	for i in xrange(count):
		if gravity_enabled:
			id = 'ent_%03d'%i
		else:
			id = ''
		e = ent.create_orbiter(id,random.uniform(pos_high,pos_low),random.uniform(mass_high,mass_low))
		entities.append(e)
	return entities

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

	def calc_gravity(self,position,entities=[]):
		self.acceleration = numpy.array([0.0,0.0,0.0])
		for ent in entities:
			if ent.id == self.id:
				continue
			rabs = numpy.linalg.norm(ent.position - position)
			g_abs = G*ent.mass*1/(rabs**2)
			g = g_abs*(ent.position - position)/rabs
			self.acceleration = self.acceleration + g
		return self.acceleration
			

	def propogate_linear(self,dt):
		self.position = self.position + dt*self.velocity
		self.velocity = self.velocity + dt*self.acceleration
		self.position_history.pop(0)
		self.position_history.append(self.position)
		
	def propogate_rk4(self,dt,entities):
	
		kr[0] = self.velocity
		kv[0] = self.calc_gravity(self.position,entities)
		kr[1] = self.velocity+kv[0]*dt/2
		kv[1] = self.calc_gravity(self.position+kr[0]*dt/2,entities)
		kr[2] = self.velocity+kv[1]*dt/2
		kv[2] = self.calc_gravity(self.position+kr[1]*dt/2,entities)
		kr[3] = self.velocity+kv[2]*dt
		kv[3] = self.calc_gravity(self.position+kr[2]*dt,entities)
		
		self.position = self.position + dt/6.0*(kr[0] + 2*kr[1] + 2*kr[2] + kr[3])
		self.velocity = self.velocity + dt/6.0*(kv[0] + 2*kv[1] + 2*kv[2] + kv[3])	
		
		
	def create_orbiter(self,id,distance,mass,color=[1.0,1.0,0.0]):
		position = self.position+numpy.array([distance,0,0])
		velocity_abs = numpy.sqrt(G*self.mass / numpy.linalg.norm(self.position-position))
		velocity = (self.position-position)/numpy.linalg.norm(self.position-position) * velocity_abs
		velocity = numpy.array([-1*velocity[1],velocity[0],velocity[2]]) + self.velocity
		acceleration = numpy.array([0.0,0.0,0.0])
		return entity(id,position,velocity,acceleration,mass,color)

	
	def draw(self):
		def pairwise(iterable):
			"s -> (s0,s1), (s1,s2), (s2, s3), ..."
			a, b = tee(iterable)
			next(b, None)
			return izip(a, b)
		glPushMatrix()
		glTranslatef(*self.position.tolist())
		mass_scale = scale+self.mass*0.0001
		glScaled(mass_scale,mass_scale,mass_scale)
		glColor3f(*self.color)
		glutWireSphere(1.0,10,10)
		glPopMatrix()
		if display_history:
			glPushMatrix()
			for pos, pos_next in pairwise(self.position_history):
				if pos is not None and pos_next is not None:
					glBegin(GL_LINES)
					glVertex3f(*pos.tolist())
					glVertex3f(*pos_next.tolist())
					glEnd()
			glPopMatrix()
			
		if display_kinetic:
			glPushMatrix()
			glColor3f(1.0,0.0,1.1)
			glBegin(GL_LINES)
			glVertex3f(*self.position.tolist())
			glVertex3f(*(self.position+self.velocity).tolist())
			glEnd()
			glPopMatrix()
			
		if display_acceleration:
			glPushMatrix()
			glColor3f(0.0,1.0,1.1)
			glBegin(GL_LINES)
			glVertex3f(*self.position.tolist())
			glVertex3f(*((self.acceleration+self.position)).tolist())
			glEnd()
			glPopMatrix()
			
	
entities = []

sun2 = {'id':'sun2',
  'position':numpy.array([200.0,0.0,0.0]),
  'velocity':numpy.array([0.0,5000.0,0.0]),
  'acceleration':numpy.array([0.0,0.0,0.0]),
  'mass':100000.0,
  'color':[1.0,1.0,0.0]}
  
sun = {'id':'sun',
  'position':numpy.array([0.0,0.0,0.0]),
  'velocity':numpy.array([0.0,0.0,0.0]),
  'acceleration':numpy.array([0.0,0.0,0.0]),
  'mass':100000.0,
  'color':[1.0,0.0,0.0]}
  

entities.append(entity(**sun))
sun3 = entities[0].create_orbiter('sun3',1000,100)
entities.append(sun3)
sun4 = entities[1].create_orbiter('moon',10,0.01,color=[1.0,0.0,0.0])
entities.append(sun4)

entities.append(sun3)

for e in orbit_generate(entities[0],count=0,gravity_enabled=True):
	entities.append(e)

for e in entity_generator.generate(count=entity_count,color=[1.0,0.0,0.0],start_position=numpy.array([-20.0,0.0,0.0]),gravity_enabled=True):
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

	gluPerspective(90.0, float(Width)/float(Height), 0.1, 100000000000000000.0)
	glMatrixMode(GL_MODELVIEW)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
	if Height == 0: 					# Prevent A Divide By Zero If The Window Is Too Small 
		Height = 1
	glMatrixMode(GL_MODELVIEW)
	glViewport(0, 0, Width, Height) 	# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(90.0, float(Width)/float(Height), 0.1, 100000000000000000.0)
	glMatrixMode(GL_MODELVIEW)


# The main drawing function. 
def DrawGLScene():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(camera_x,0.0,camera_z,xpos,0.0,0.0,0.0,1.0,0.0)	
	glPushMatrix()
	for ent in entities:
		if not paused:
			#ent.calc_gravity(ent.position,entities)
			#ent.propogate_linear(dt)
			ent.propogate_rk4(dt,entities)
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
	global display_acceleration
	global display_kinetic
	global paused
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()
	
	if args[0] == 'w':
		zoom = zoom + 50
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 's':
		zoom = zoom - 50
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'q':
		view_angle = view_angle + 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'e':
		view_angle = view_angle - 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'q':
		view_angle = view_angle + 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'e':
		view_angle = view_angle - 0.02
		camera_z = numpy.cos(view_angle)*zoom
		camera_x = numpy.sin(view_angle)*zoom
		
	if args[0] == 'h':
		if display_history:
			display_history = False
		else:
			display_history = True
			
	if args[0] == 'j':
		if display_acceleration:
			display_acceleration = False
		else:
			display_acceleration = True
			
	if args[0] == 'k':
		if display_kinetic:
			display_kinetic = False
		else:
			display_kinetic = True
		
	if args[0] == 'p':
		if paused:
			paused = False
		else:
			paused = True	


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
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(screensize[0], screensize[1])
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("project-blossom")
	glutDisplayFunc(DrawGLScene)
	# Uncomment this line to get full screen.
	#glutFullScreen()
	glutIdleFunc(DrawGLScene)
	glutReshapeFunc(ReSizeGLScene)
	glutMouseFunc(mouse)
	glutKeyboardFunc(keyPressed)
	InitGL(screensize[0], screensize[1])
	# Start Event Processing Engine 
	glutMainLoop()
		
		
if __name__ == "__main__":
	main()

