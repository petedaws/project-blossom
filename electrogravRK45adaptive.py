from __future__ import division
from pylab import *
import os

#Evaluates the derivative functions
def derivs(time, last_values, properties, alpha):
    particle_num = size(last_values, axis = 1)
    spatial_dims = size(last_values, axis = 0)/2.
    grad = zeros((spatial_dims * 2, particle_num))

    for j in arange(particle_num):
        #Calc position derivative
        grad[0, j] = last_values[1, j]
        grad[2, j] = last_values[3, j]
        grad[4, j] = last_values[5, j]
        
        #Calc velocity derivative
        field_sum = calc_field(last_values, j, properties)
        grad[1, j] = properties[1, j] / properties[0, j] * alpha * field_sum[0]
        grad[3, j] = properties[1, j] / properties[0, j] * alpha * field_sum[1]
        grad[5, j] = properties[1, j] / properties[0, j] * alpha * field_sum[2]

    return grad



#Evaluate the summuation to calculate the field at one particle due to all the others
def calc_field(last_values, at_particle, properties):
    particle_num = size(last_values, axis = 1)
    spatial_dims = size(last_values, axis = 0)/2
    #Calculate summation
    field_sum = zeros(spatial_dims)
    denominator = zeros(1)
    
    for i in arange(particle_num):
        if i != at_particle:
            delx1 = last_values[0, at_particle] - last_values[0, i]
            delx2 = last_values[2, at_particle] - last_values[2, i]
            delx3 = last_values[4, at_particle] - last_values[4, i]
            denominator = ((delx1**2 + delx2**2 + delx3**2)**(3./2.))
            
            field_sum[0] = field_sum[0] + delx1 * properties[1, i] / denominator
            field_sum[1] = field_sum[1] + delx2 * properties[1, i] / denominator
            field_sum[2] = field_sum[2] + delx3 * properties[1, i] / denominator
    
    return field_sum


#Energy calculator
def energy_calc(last_values, properties, alpha):
    #Potential energy
    pot = zeros(1)
    for i in range(size(last_values, 1)):
        for j in range(i+1, size(last_values, 1)):
            delx1 = last_values[0, i] - last_values[0, j]
            delx2 = last_values[2, i] - last_values[2, j]
            delx3 = last_values[4, i] - last_values[4, j]
            denominator = (delx1**2 + delx2**2 + delx3**2)**(1/2)
            pot = pot + alpha * properties[1, i] * properties[1, j] / denominator

    #Kinetic energy
    kin = zeros(1)
    for i in range(size(last_values, 1)):
        speed = (last_values[1, i]**2 + last_values[3, i]**2 + last_values[5, i]**2)**(1/2)
        kin = kin + 0.5 * properties[0, i] * speed**2

    #Total energy
    tot_energy = pot + kin

    return [pot, kin, tot_energy]


#Coefficients used in the Runge-Kutta loop
def solver_coef():
    a = zeros(7)
    b = zeros((7, 7))
    c = zeros(7)
    cstar = zeros(7)

    a[0], a[1], a[2], a[3], a[4], a[5], a[6] = 0, 1/5, 3/10, 4/5, 8/9, 1, 1
    b[1, 0] = 1/5
    b[2, 0], b[2, 1] = 3/40, 9/40
    b[3, 0], b[3, 1], b[3, 2] = 44/45, -56/15, 32/9
    b[4, 0], b[4, 1], b[4, 2], b[4, 3] = 19372/6561, -25360/2187, 64448/6561, -212/729
    b[5, 0], b[5, 1], b[5, 2], b[5, 3], b[5, 4] = 9017/3168, -355/33, 46732/5247, 49/176, -5103/18656
    b[6, 0], b[6, 1], b[6, 2], b[6, 3], b[6, 4], b[6, 5] = 35/384, 0, 500/1113, 125/192, -2187/6784, 11/84
    c[0], c[1], c[2], c[3], c[4], c[5], c[6] = 5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100, 1/40
    cstar[0], cstar[1], cstar[2], cstar[3], cstar[4], cstar[5], cstar[6] = 35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0
    
    return [a, b, c, cstar]


#The Runge-Kutta code
def rkstep(sol, time, h, k7):

    k1 = k7
    k2 = h * derivs(time +  a[1] * h, sol + b[1, 0] * k1, properties, alpha)
    k3 = h * derivs(time +  a[2] * h, sol + b[2, 0] * k1 + b[2, 1] * k2, properties, alpha)
    k4 = h * derivs(time +  a[3] * h, sol + b[3, 0] * k1 + b[3, 1] * k2 + b[3, 2] * k3, properties, alpha)
    k5 = h * derivs(time +  a[4] * h, sol + b[4, 0] * k1 + b[4, 1] * k2 + b[4, 2] * k3 + b[4, 3] * k4, properties, alpha)
    k6 = h * derivs(time +  a[5] * h, sol + b[5, 0] * k1 + b[5, 1] * k2 + b[5, 2] * k3 + b[5, 3] * k4 + b[5, 4] * k5, properties, alpha)
    k7 = h * derivs(time +  a[6] * h, sol + b[6, 0] * k1 + b[6, 1] * k2 + b[6, 2] * k3 + b[6, 3] * k4 + b[6, 4] * k5 + b[6, 5] * k6, properties, alpha)
    sol = sol + c[0] * k1 + c[1] * k2 + c[2] * k3 + c[3] * k4 + c[4] * k5 + c[5] * k6 + c[6] * k7 
    solstar = sol + cstar[0] * k1 + cstar[1] * k2 + cstar[2] * k3 + cstar[3] * k4 + cstar[4] * k5 + cstar[5] * k6 + cstar[6] * k7

    return [sol, solstar, k7]


#Make the colour & size array for the particles
def plot_props(properties):
    particle_colours = zeros((size(properties, 1), 4))
    colour_strength = -1/(abs(properties[1,:]) + 2) + 1
    particle_colours[:, 3] = colour_strength[:]
    
    for idx in arange(size(properties, 1)):
        #Make -ve charge blue, +ve charge red
        if properties[1, idx] >= 0:
            particle_colours[idx, 0] = 1
        else:
            particle_colours[idx, 2] = 1

    particle_size = properties[0, :]**(2/3) * 4

    return [particle_colours, particle_size]


#Calculate net momentum of the system
def momentum_calc(sol, properties):
    px = 0.0
    py = 0.0
    pz = 0.0
    for i in range(size(sol, 1)):
        px = px + sol[1, i] * properties[0, i]
        py = py + sol[3, i] * properties[0, i]
        pz = pz + sol[5, i] * properties[0, i]
    
    return [px, py, pz]


#Initial conditions
def initial_conditions(spatial_dims, particle_num, properties):
    sol = zeros((spatial_dims * 2, particle_num))
    v1bias = 0.1
    v2bias = -0.70
    #Patticle 0
    sol[0, 0] = 0.0 #x1
    sol[1, 0] = 0.0 + v1bias #v1
    sol[2, 0] = 0.0 #x2
    sol[3, 0] = 0.0 + v2bias #v2
    sol[4, 0] = 0.0 #x3
    sol[5, 0] = 0.0 #v3
    properties[1, 0] = 50 #charge
    properties[0, 0] = 50 #mass
    #Particle 1
    sol[0, 1] = 2.0 #x1
    sol[1, 1] = 0.0 + v1bias #v1
    sol[2, 1] = 0.0 #x2
    sol[3, 1] = 6.0 + v2bias #v2
    sol[4, 1] = 0.0 #x3
    sol[5, 1] = 0.0 #v3
    properties[1, 1] = 20 #charge
    properties[0, 1] = 20 #mass
    #Particle 2
    sol[0, 2] = 1.7 #x1
    sol[1, 2] = 0.0 + v1bias #v1
    sol[2, 2] = 0.0 #x2
    sol[3, 2] = -2.5 + v2bias #v2
    sol[4, 2] = 0.0 #x3
    sol[5, 2] = 0.0 #v3
    properties[1, 2] = 2 #charge
    properties[0, 2] = 2 #mass
    #Particle 3
    sol[0, 3] = -3.0 #x1
    sol[1, 3] = 0.0 + v1bias #v1
    sol[2, 3] = 0.0 #x2
    sol[3, 3] = -4.5 + v2bias #v2
    sol[4, 3] = 0.0 #x3
    sol[5, 3] = 0.0 #v3
    properties[1, 3] = 10 #charge
    properties[0, 3] = 10 #mass
    #Particle 4
    sol[0, 4] = -2.7 #x1
    sol[1, 4] = 0.0 + v1bias #v1
    sol[2, 4] = 0.0 #x2
    sol[3, 4] = 0.5 + v2bias #v2
    sol[4, 4] = 0.0 #x3
    sol[5, 4] = 0.0 #v3
    properties[1, 4] = 1 #charge
    properties[0, 4] = 1 #mass
    #Particle 5
    sol[0, 5] = -1.0 #x1
    sol[1, 5] = 0.0 + v1bias #v1
    sol[2, 5] = 0.0 #x2
    sol[3, 5] = -7.0 + v2bias #v2
    sol[4, 5] = 0.0 #x3
    sol[5, 5] = 0.0 #v3
    properties[1, 5] = 2 #charge
    properties[0, 5] = 2 #mass 
    #Particle 6
    sol[0, 6] = 0.0 #x1
    sol[1, 6] = -5.0 + v1bias #v1
    sol[2, 6] = 2.5 #x2
    sol[3, 6] = 0.0 + v2bias #v2
    sol[4, 6] = 0.0 #x3
    sol[5, 6] = 0.0 #v3
    properties[1, 6] = 2 #charge
    properties[0, 6] = 2 #mass 
    
    return sol

    

###############################################################################
#Start of script. The script calculates in 3 spatial dims, but only plots 2.
t_min = 0.0
t_max = 10.0
epsilon = 1.0e-1
vdivx_errscale = 1
safety = 0.90

particle_num = 7
spatial_dims = 3

slice_interval = 0.01
slices_per_plot = 1
total_slices = floor((t_max - t_min) / slice_interval) + 1

#sol and associated arrays store things as [x1,v1,x2,v2,x3,v3]
data = zeros((total_slices, spatial_dims * 2, particle_num))
time_array = zeros(total_slices)


#Initial conditions
#Properties[0, :] is mass
#properties[1, :] is charge
properties = ones((2, particle_num))
sol = initial_conditions(spatial_dims, particle_num, properties)
data[0, :, :] = sol[:, :]

#Calc net momentum and print
pnet = momentum_calc(sol, properties)
print 'Net momentum = ' + str(pnet)

#The field constant. -ve for gravity, +ve for electric charges
alpha = -1.

#System energy
energy = ones((3, total_slices))
energy[:, 0] = energy_calc(sol, properties, alpha)

#Get solver coefficients
[a, b, c, cstar] = solver_coef()

t = t_min
cnt = 0
cnt1 = 0
slice_num_temp = -1

#Allows you to scale the error for x and v differently
err_scale = ones((spatial_dims * 2, particle_num))
err_scale[1, :] = vdivx_errscale * err_scale[1, :]
err_scale[3, :] = vdivx_errscale * err_scale[3, :]
err_scale[5, :] = vdivx_errscale * err_scale[5, :]

#Dormand - Prince RK loop
h_try = 0.001
h = h_try
#Dormand - Prince has "first same as last" property.
k7 = h * derivs(t, sol, properties, alpha)

while t < t_max:
    
    [soltemp, solstar, k7temp] = rkstep(sol, t, h, k7)
    
    delta = soltemp - solstar
    max_delta = epsilon * err_scale
    err_prop = abs(delta) / abs(max_delta)
    maxprop = err_prop.max()
    maxprop_idx = err_prop.argmax()
    if maxprop > 1:
        #Decrease step size
        htemp = safety * h * abs(max_delta.ravel()[maxprop_idx] / delta.ravel()[maxprop_idx])**0.2
        h = max(0.1 * h, htemp)
    else:
        #Increase step size
        htemp = safety * h * abs(max_delta.ravel()[maxprop_idx] / delta.ravel()[maxprop_idx])**0.25
        h = min(10 * h, htemp, slice_interval)
        #Update vals
        sol = soltemp
        k7 = k7temp
        t = t + h

    #Print update to the terminal every so often
    slice_num = floor(t / slice_interval)
    if cnt1 % 500 == 0:
        print 'Slice:' + str(int(slice_num)) + ', t = ' + str(t) + ', h = ' +str(h)

    cnt1 = cnt1 + 1
    #Record data after defined time interval
    if slice_num != slice_num_temp:
        data[cnt, :, :] = sol[:, :]
        energy[:, cnt] = energy_calc(sol, properties, alpha)
        time_array[cnt] = t
        cnt = cnt + 1
        slice_num_temp = slice_num



#Plot energy
plot(time_array[:cnt], energy[0, :cnt], '--', time_array[:cnt], energy[1, :cnt], '.', time_array[:cnt], energy[2, :cnt])
xlabel('t')
ylabel('energy')
legend(('potential', 'kinetic', 'total'), loc = 'lower left')
title('Total energy of the system')
savefig('Images/system_energy.png', dpi = 300)
show()
clf()

#Make colour array
[particle_colours, particle_size] = plot_props(properties)

#Plot pictures
destpath = 'Images/'
filename = '%03d'
filetype = '.png'
res_dpi = 150

for a in arange(cnt/slices_per_plot):
    x_vals = data[a * slices_per_plot, 0, :cnt]
    y_vals = data[a * slices_per_plot, 2, :cnt]

    scatter(x_vals, y_vals, s = particle_size, c = particle_colours, edgecolors = particle_colours)
    xlabel('x')
    ylabel('y')
    axis([-5.0, 5.0, -5.0, 5.0])
    axes().set_aspect('equal')
    title('Interaction of "charged" particles')
    fullfilename = destpath + str(filename % a) + filetype
    savefig(fullfilename, dpi = res_dpi)
    clf()

#Make a movie
movie_name = ' gravo_movie.mp4'
savedPath = os.getcwd()
os.chdir(destpath)
movie_command = 'ffmpeg -qscale 1 -r 25 -i ' + filename + filetype + movie_name
os.system(movie_command)
os.chdir(savedPath)




