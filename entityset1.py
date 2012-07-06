import numpy
e1 = {'id':'e1',
      'position':numpy.array([100.0,0.0,0.0]),
      'velocity':numpy.array([0.0,-1000.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':1.0}

e2 = {'id':'e2',
      'position':numpy.array([-100.0,0.0,0.0]),
      'velocity':numpy.array([0.0,1500.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':1.0}



e3 = {'id':'e3',
      'position':numpy.array([0.0,100.0,0.0]),
      'velocity':numpy.array([-.0,0.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':1.0}


e4 = {'id':'e4',
      'position':numpy.array([100.0,100.0,0.0]),
      'velocity':numpy.array([0.0,-1000.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':1.0}


e5 = {'id':'e5',
      'position':numpy.array([0.0,0.0,0.0]),
      'velocity':numpy.array([0.0,0.0,0.0]),
      'acceleration':numpy.array([0.0,0.0,0.0]),
      'mass':5000.0}

entities = [e1,e2,e3,e4,e5]
