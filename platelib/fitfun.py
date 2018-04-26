from plateread import Plate_data 
import numpy as np


def exp_rise(t,a,b,k):
    return b - a*np.exp(-k*t)

def linear(t,a,b):
    return t*a + b

def quadratic(t,a,b,c):
    return a*np.power(t,2)+b*t+c

def sigmoidal_auto(t,a,b,k):
	return (a + b)/( 1 + (b/a)*np.exp((a+b)*k*t))


# TODO: 
# 1. Fit all wells in a plate_data instance locally 
# 2. Fit all wells in a plate_data instance globally in group
# 3. Fit all groups globally
# 4. Plots with the associated fits
# 5. Report on fitting quality        
# Note that the actually fitting function could be done in Cython         
    
class fit_plate(Plate_data):
    pass  



import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters, report_fit

def gauss(x, amp, cen, sigma):
    "basic gaussian"
    return amp*np.exp(-(x-cen)**2/(2.*sigma**2))

def gauss_dataset(params, i, x):
    """calc gaussian from params for data set i
    using simple, hardwired naming convention"""
    amp = params['amp_%i' % (i+1)].value
    cen = params['cen_%i' % (i+1)].value
    sig = params['sig_%i' % (i+1)].value
    return gauss(x, amp, cen, sig)

def objective(params, x, data):
    """ calculate total residual for fits to several data sets held
    in a 2-D array, and modeled by Gaussian functions"""
    ndata, nx = data.shape
    resid = np.zeros_like(data,dtype=np.float)
    # make residual per data set
    for i in range(ndata):
        resid[i, :] = data[i, :] - gauss_dataset(params, i, x)
    # now flatten this to a 1D array, as minimize() needs
    return resid.flatten()

# create 5 datasets
'''
x  = np.linspace( -1, 2, 151)
data = []
for i in np.arange(5):
    amp   =  0.60 + 9.50*np.random.rand()
    cen   = -0.20 + 1.20*np.random.rand()
    sig   =  0.25 + 0.03*np.random.rand()
    dat   = gauss(x, amp, cen, sig) + np.random.normal(size=len(x), scale=0.1)
    data.append(dat)

# data has shape (5, 151)
data = np.array(data)
assert(data.shape) == (5, 151)

# create 5 sets of parameters, one per data set
fit_params = Parameters()
for iy, y in enumerate(data):
    fit_params.add( 'amp_%i' % (iy+1), value=0.5, min=0.0,  max=200)
    fit_params.add( 'cen_%i' % (iy+1), value=0.4, min=-2.0,  max=2.0)
    fit_params.add( 'sig_%i' % (iy+1), value=0.3, min=0.01, max=3.0)

# but now constrain all values of sigma to have the same value
# by assigning sig_2, sig_3, .. sig_5 to be equal to sig_1
for iy in (2, 3, 4, 5):
    fit_params['sig_%i' % iy].expr='sig_1'

# run the global fit to all the data sets
result = minimize(objective, fit_params, args=(x, data))
report_fit(result.params)

# plot the data sets and fits
plt.figure()
for i in range(5):
    y_fit = gauss_dataset(result.params, i, x)
    plt.plot(x, data[i, :], 'o', x, y_fit, '-')

plt.show()
'''
