import random
import numpy

def generate(count=10):
	entities = []
	pos_high = 100.0
	pos_low = -100.0
	vel_high = 10000.0
	vel_low = -10000.0
	mass_high = 100.0
	mass_low = 1.0
	for i in xrange(count):
		e = {'id':'ent_%03d'%i,
		  'position':numpy.array([random.uniform(pos_high,pos_low),random.uniform(pos_high,pos_low),random.uniform(pos_high,pos_low)]),
		  'velocity':numpy.array([random.uniform(vel_high,vel_low),random.uniform(vel_high,vel_low),random.uniform(vel_high,vel_low)]),
		  'acceleration':numpy.array([0.0,0.0,0.0]),
		  'mass':random.uniform(mass_high,mass_low)}
		entities.append(e)
	return entities
		
if __name__ == "__main__":
	print generate(10)