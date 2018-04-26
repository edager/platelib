#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from string import ascii_uppercase as A_up 

# Read in data from a bmg or tecan platereader
   
# TODO:
# 1. Extract metadata/header from data files  

def read_plate(filename,replicates=3,rep_direction='hori',time_unit='hours', 
               platereader='bmg',transposed=True):
    '''
    Reads in data from a CSV file from a BMG or Tecan platereader and returns a platedata object.
    
    :param filename: Path to filename as a string
    :param replicates: The number of replicates per sample, excepts a positive integer.
    :param rep_direction: The directions replicates is in. Only 'hori' and 'vert' are accepted directions, 'hori' if replicates are going from left to rigth 'vert' from replicates going from top to bottom. 
    :param time_unit: The time unit one would like to have, accepted values are: 'seconds','minutes','hours','days'  
    :param platereader: The plate reader used to collect the data. Only 'bmg' and 'tecan' are accepted platereaders
    :param transposed: Wether the wells are in column (True) or row format (False).   
    '''
    Timepars = ['seconds','minutes','hours','days']
    Timefactor = [1.0, 60.0, 3600.0, 86400.0]
    
    if time_unit not in Timepars:
        raise ValueError('"{}" is not a supported unit'.format(time_unit)) 
    
    if rep_direction not in ('vert','hori'):
        raise ValueError('"{}" is not a valid direction, only "vert" and "hori" are'.format(rep_direction)) 
    
    if platereader not in ('bmg','tecan'):
        raise ValueError('"{}" platereader format is not supported , only "bmg" and "tecan" are'.format(platereader))
    
    if filename.lower().endswith(('.xls','.xlsx','.csv')) != True:
        raise ValueError('"{}" is not a supported filetype, only ".xls",".xlsx", and ".csv" are'.format(filename))
    
    if platereader == 'bmg': 
        if transposed==True:
            df = read_transposed_bmg(filename)
        else:
            df = read_untransposed_bmg(filename)
    
    else:   
        df = read_tecan(filename)
    
    for a,b in zip(Timepars,Timefactor):
        if time_unit == a:
            df.index = df.index/b
            df.index.name = a
    
    return Plate_data(df, replicates, rep_direction)

def read_transposed_bmg(filename):
    '''
    Reads in transposed data from a BMG platereader and returns a pandas DataFrame object.
    
    :param filename: Path to filename as a string   
    '''
    
    if filename.lower().endswith(('.xls','.xlsx')):    
        df = pd.read_excel(filename,
                          index_col = 1,
                          skiprows=[0,1,2,3,4,5,6,7,8,10])
    else:
        df = pd.read_table(filename,
                          sep=None, index_col = 1,
                          skiprows=[0,1,2,3,4,6],engine='python')
            
    df.drop('Well', axis=1, inplace=True)
    return df
        
def read_untransposed_bmg(filename):        
    '''
    Reads in untransposed data from a BMG platereader and returns a pandas DataFrame object.
    
    :param filename: Path to filename as a string   
    '''
    
    if filename.lower().endswith(('.xls','.xlsx')):
        df = pd.read_excel(filename,skiprows=range(10))
    else:
        df = pd.read_table(filename,sep=None,skiprows=range(6),engine='python')
     
    df.drop(df.columns[1],axis=1,inplace=True)
    df = df.transpose()
    df.columns = df.iloc[0,:]
    df.drop(df.index[0],axis=0,inplace=True)
    df = df.astype(np.int)
    df.index = df.index.astype(np.int)    
    return df

def read_tecan(filename):
    '''
    Reads in untransposed data from a tecan platereader and returns a pandas DataFrame object.
    
    :param filename: Path to filename as a string   
    '''
     
    d = pd.read_excel(filename, skiprows=range(62), skipfooter=3,header=None)
    d = d.transpose() 
    l = np.where(d.iloc[0,:] == u'Temp. [\xb0C]')[0]
    d = d.drop(labels=np.concatenate((l-3,l-4)), axis=1)
    d = d.dropna(how='any')
       
    df = pd.DataFrame(data=(d.loc[1:, l + 1]).values,
                      index=d.loc[1:,l[0]-1],
                      columns=d.loc[0, l - 2].values) 
    return df

# TODO:
# There must be a cleaner way to reorder the columns 
def vert_order(cols,reps):
    '''
    Helper function to reorder data if vertical replicates were made.
    
    :param cols: List-like object of columns names (wells) all assumed to have the form 'A12'.
    :param reps: Oositive integer number of replicates.  
    '''
    new_col_order = []
    for a in cols:
        # well already there ?
        if a not in new_col_order:
            # appends the well and the replicate number of the wells below it 
            for i in [b+a[1:] for b in A_up[A_up.index(a[0]):A_up.index(a[0])+reps]]:
                new_col_order.append(i)
    return new_col_order             

# TODO:
# 1. use pandas multiindexing to store the replicates in groups 
    # df.loc[:, pd.IndexSlice[:, ['0A','3B']]]
class Plate_data():
    '''
    Class for containing data from a platereader assay. 
 	
	:param data: A pandas DataFrame with time points as index and wells as columns
	:param replicates: Positive integer of replicates, assuming equal number of replicates of all samples     
    '''
    
    def __init__(self, data, replicates=3,rep_direction='hori'):
           
        self.data = data
        self.rep = replicates
        self.rep_dir = rep_direction
        
        if self.rep_dir == 'vert':
            self.data = self.data[vert_order(self.data.columns.values,self.rep)]            
            
        self.wells = self.data.columns.values
        self.times = self.data.index.values
        
    def __getitem__(self, key):

        # Access self.data by (integer) index of column    
        if isinstance(key, slice):
            return self.data.iloc[:, key.start:key.stop:key.step]
        elif isinstance(key, int):
            return self.data.iloc[:, key]
        
        # Access self.data by name of column
        elif isinstance(key, str):
            return self.data.loc[:, key]
        elif isinstance(key, list):
            if sum([isinstance(i, str) for i in key]) == len(key):
                return self.data.loc[:, key]
     
        else:
            raise TypeError, "Invalid argument type."
    
    # returns the number of columns i.e. samples        
    def __len__(self):
        return len(self.wells)

    def to_a_dataframe(self):
        '''
        Returns the data as a pandas dataframe with times as indexes 				
        '''		
        return self.data
    
    def to_a_csv(self,path):
        '''
        Returns the data as a pandas dataframe with times as indexes 				
        
        :param path: path to store output at
        '''
        self.data.to_csv(path) 
    
    def plot_data(self,titles=None,sharey=True):
        '''
        Plots the number the number of sample i.e. replicates/wells in the data 
        set. 
        
        :param titles: List-like object of subtitles 
        :param sharey: Boolean, default is True, where the y-axis limits are identical. If False y-axis limits are given by matplotlib defaults.     
        '''        
        if titles == None:
            titles = [None]*(int(np.ceil(len(self.wells)/float(self.rep))))
        
        
        nplots = int(len(self)/float(self.rep)) 
        rows =  int(np.ceil(nplots/5.0))
        fig = plt.figure(figsize=(15,rows*15),dpi=100,tight_layout=True)
        
        # Keeping track of the biggest range on y-axis 
        max_ylim = [10e6,0]  
                
        for i in range(nplots):
            axes = fig.add_subplot(rows,5,i+1)
            off_set = i*self.rep
            iC = self.data.iloc[:,range(off_set,off_set+self.rep)]
            iC.plot(ax=axes,style='o', title=titles[i])
            
            if sharey == True: 
            
                low_y, high_y =  axes.get_ylim()
            
                if low_y < max_ylim[0] or high_y > max_ylim[1]:  
                    max_ylim[0], max_ylim[1] = min((max_ylim[0],low_y)), max((max_ylim[1],high_y))
                    for ax in fig.get_axes():
                        ax.set_ylim(tuple(max_ylim))
            
                axes.set_ylim(tuple(max_ylim))
                
		fig.show()
        


                

