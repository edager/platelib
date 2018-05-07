from __future__ import division 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plateread import Plate_data
from scipy.optimize import curve_fit 
from lmfit import minimize, Parameters, report_fit

def exp_rise(t,a,b,k):
    return b - a*np.exp(-k*t)

def linear(t,a,b):
    return t*a + b

def quadratic(t,a,b,c):
    return a*np.power(t,2)+b*t+c

def sigmoidal_auto(t,a,b,k):
	return (a + b)/( 1 + (b/a)*np.exp((a+b)*k*t))


def sigmoid(x,y0,L,k,x_half):
    return y0 + (L/(1+np.exp(-k*(x-x_half))))


def fit_fun(func,df,bounds=([0,0,0,0],[1,50,10,65])):
	
	opt_para = []
	std_para = []
	
	t = df.iloc[:,i].index.values
	
	for i in range(len(df.columns)):
		popt, pcov = curve_fit(sigmoid,
                               t, 
                               wt.iloc[:,i].values/1000.0,
                               bounds=bounds)
        opt_para.append(popt)
        std_para.append(np.sqrt(np.diag(pcov)))

	return opt_para, std_para

# TODO: 
# 1. Fit all wells in a plate_data instance locally 
# 2. Fit all wells in a plate_data instance globally in group
# 3. Fit all groups globally
# 4. Plots with the associated fits
# 5. Report on fitting quality        
# Note that the actually fitting function could be done in Cython         
    
class fit_plate(Plate_data):
    pass  
