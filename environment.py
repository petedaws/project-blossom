import numpy
import time
import pygame
import entityset1
import entity_generator

G = 98000
dt = 0.0001
screensize = (1024,768)

class entity():
	def __init__(self,id,position,velocity,acceleration,mass):
		self.id = id
		self.position = position 
		self.velocity = velocity
		self.acceleration = acceleration
		self.mass = mass

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


if __name__ == "__main__":

	pygame.init()
	screen = pygame.display.set_mode(screensize)
	screen.fill((255,255,255))
	pygame.display.update()
	xoffset = screensize[0]/2
	yoffset = screensize[1]/2

	entities = []
	
	sun = {'id':'sun',
      'position':numpy.array([0.0,0.0,0.0]),
      'velocity':numpy.array([0.0,0.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':50000.0}
	
	entities.append(entity(**sun))
	
	for e in entity_generator.generate(10):
		entities.append(entity(**e))

	
	while(1):
		screen.fill((255,255,255))	
		for ent in entities:
			ent.calc_gravity(entities)
			ent.propogate_linear(dt)
			#time.sleep(dt)

			if ent.id == 'e1':
				None#print ent.position,int(ent.position[0]+xoffset),int(ent.position[1]+yoffset)
				
			
			pygame.draw.circle(screen, (0,0,0), (int(ent.position[0]+xoffset),int(ent.position[1]+yoffset)), 5, 5)
		pygame.display.update()
		
