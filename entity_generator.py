import random
import numpy

def generate(count=10,color=[0,0,0],start_position=numpy.array([0,0,0]),gravity_enabled=False):
	entities = []
	pos_low = -500.0
	pos_high = 500.0
	vel_high = 1.0
	vel_low = 1.0
	mass_high = 10000.0
	mass_low = 10000.0
	vel_factor = 98000.0 * 100000.0
	for i in xrange(count):
		if gravity_enabled:
			id = 'ent_%03d'%i
		else:
			id = ''
		position = start_position+numpy.array([random.uniform(pos_high,pos_low),random.uniform(pos_high,pos_low),random.uniform(pos_high,pos_low)])
		velocity_abs = numpy.sqrt(random.uniform(vel_low,vel_high) * vel_factor / numpy.linalg.norm(start_position-position))
		velocity = (start_position-position)/numpy.linalg.norm(start_position-position) * velocity_abs
		velocity = numpy.array([-1*velocity[1],velocity[0],velocity[2]])
		e = {'id':id,
		  'position':position,
		  'velocity':velocity,
		  'acceleration':numpy.array([0.0,0.0,0.0]),
		  'mass':random.uniform(mass_high,mass_low),
		  'color':color}
		entities.append(e)
	return entities
		
if __name__ == "__main__":
	print generate(10)