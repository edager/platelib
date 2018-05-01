#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from string import ascii_uppercase as A_up
from xlrd import open_workbook
 

# Read in data from a bmg or tecan platereader
   
# TODO:
# 1. Extract metadata/header from data files
# 2. Clean this function, likely by turning something some parts into independent functions    

def read_plate(filename,replicates=3,rep_direction='hori',time_unit='hours',named_samples=[], 
               platereader='bmg',transposed=True):
    '''
    Reads in data from a CSV file from a BMG or Tecan platereader and returns a platedata object.
    
    :param filename: Path to filename as a string
    :param replicates: The number of replicates per sample, expects a positive integer.
    :param rep_direction: The directions replicates is in. Only 'hori' and 'vert' are accepted directions, 'hori' if replicates are going from left to rigth 'vert' from replicates going from top to bottom. 
    :param time_unit: The time unit one would like to have, accepted values are: 'seconds','minutes','hours','days'  
    :param platereader: The plate reader used to collect the data. Only 'bmg' and 'tecan' are accepted platereaders
    :param transposed: Wether the wells are in column (True) or row format (False).   
    '''
    

    if filename.lower().endswith(('.xls','.xlsx','.csv')) != True:
        raise ValueError('"{}" is not a supported filetype, only ".xls",".xlsx", and ".csv" are'.format(filename))

    if rep_direction not in ('vert','hori'):
        raise ValueError('"{}" is not a valid direction, only "vert" and "hori" are'.format(rep_direction)) 
    
    Timepars = ['seconds','minutes','hours','days']
    Timefactor = [1.0, 60.0, 3600.0, 86400.0]	

    if time_unit not in Timepars:
        raise ValueError('"{}" is not a supported unit'.format(time_unit))

    if type(named_samples) != list:
		raise TypeError('Expected a "list" for named_samples got a "{}"'.format(type(named_samples)))  

    if platereader not in ('bmg','tecan'):
        raise ValueError('"{}" platereader format is not supported , only "bmg" and "tecan" are'.format(platereader))
    
    if platereader == 'bmg': 
        if transposed==True:
            df = read_transposed_bmg(filename)
        else:
            df = read_untransposed_bmg(filename)

    else:   
        df = read_tecan(filename)
       
    # convert to specfied time units:      
    for a,b in zip(Timepars,Timefactor):
        if time_unit == a:
            df.index = df.index//b
            df.index.name = a
	
    # how many measurements at each time-point?
    multi_chrom = len(df.index.unique()) // len(df.index)
    
    # reorder according to named samples   
    if len(named_samples) != 0:
        rep_per_sample = [len(i) for i in named_samples]
        rep_per_sample.insert(0,0)
        replicates = np.cumsum(rep_per_sample)
        rep_direction = None
        df = df[[n for sample in named_samples for n in sample]] 
    
    else:
        replicates = range(0,len(df.columns)+replicates,replicates)		
    
    return Plate_data(df, replicates, rep_direction, multi_chrom)

def search_start(filename):
    '''
    Find start of data region and returns the line number by finding the line that starts with "Well".
    
    :param filename: Path to filename as a string   
    '''
    lines_to_skip = 0  
    if filename.lower().endswith(('.xls','.xlsx')):
        wb = open_workbook(filename)
        s = wb.sheets()[0]
        for r in range(s.nrows):
                lines_to_skip += 1
                c = s.cell(r,0)
                if c.value == 'Well':
                    break
    
    else:
        with open(filename, 'r') as f:
            for line in f:
                lines_to_skip += 1
                if line.startswith('Well'):
                    break
    
    return lines_to_skip
                

def read_transposed_bmg(filename):
    '''
    Reads in transposed data from a BMG platereader and returns a pandas DataFrame object.
    
    :param filename: Path to filename as a string   
    '''
    
    start = search_start(filename) 
    skiprows = range(start - 1)
    skiprows.insert(-1, start)
    
    if filename.lower().endswith(('.xls','.xlsx')):    
        df = pd.read_excel(filename,
                          index_col = 1,
                          skiprows=skiprows)
    else:
        df = pd.read_table(filename,
                          sep=None, index_col = 1,
                          skiprows=skiprows,engine='python')
            
    df.drop('Well', axis=1, inplace=True)
    return df
        
def read_untransposed_bmg(filename):        
    '''
    Reads in untransposed data from a BMG platereader and returns a pandas DataFrame object.
    
    :param filename: Path to filename as a string   
    '''
    
    skiprows = range(search_start(filename))
    if filename.lower().endswith(('.xls','.xlsx')):
        df = pd.read_excel(filename,skiprows=skiprows)
    else:
        df = pd.read_table(filename,sep=None,skiprows=skiprows,engine='python')
     
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
    raw_d = pd.read_excel(filename, skiprows=range(62), skipfooter=3,header=None)
    raw_d = raw_d.transpose() 
    i_temps = np.where(raw_d.iloc[0,:] == u'Temp. [\xb0C]')[0]
    raw_d = raw_d.drop(labels=np.concatenate((i_temps-3,i_temps-4)), axis=1)
    raw_d = raw_d.dropna(how='any')
       
    df = pd.DataFrame(data=(raw_d.loc[1:, i_temps + 1]).values,
                      index=raw_d.loc[1:,i_temps[0]-1],
                      columns=raw_d.loc[0, i_temps - 2].values) 
    return df

# TODO:
# There must be a cleaner way to reorder the columns 
def vert_order(cols,reps):
    '''
    Helper function to reorder data if vertical replicates were made.
    
    :param cols: List-like object of columns names (wells) all assumed to have the form 'A12'.
    :param reps: List of positive integer number of replicates.  
    '''
    new_col_order = []
    diff = reps[1]-reps[0]   
    for a in cols:
        # well already there ?
        if a not in new_col_order:
            # appends the well and the replicate number of the wells below it 
            for i in [b+a[1:] for b in A_up[A_up.index(a[0]):A_up.index(a[0])+diff]]:
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
    
    def __init__(self, data, replicates=3, rep_direction='hori',multi_chrom=1):
           
        self.data = data
        self.multi_chrom = multi_chrom
        self.rep = replicates
        self.rep_dir = rep_direction
        
        if self.rep_dir == 'vert':
            self.data = self.data[vert_order(self.data.columns.values,self.rep)]            
            
        self.wells = self.data.columns.values
        self.timepoints = self.data.index.values
        self.N_unique_timepoints = len(self.data.index.unique().values) 
        
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

    def to_a_dataframe(self, one_per_multi_c=False):
        '''
        Returns the data as a list of pandas dataframe(s) with times as indexes 				
        
        :param one_per_multi_c: Boolean, if 'True' one measurement per dataframe will be exported otherwise all will be exported in one dataframe.              
	    '''		
        if one_per_multi_c: 
            return [self.data.iloc[i-self.N_unique_timepoints:i] for i in range(0,self.multi_chrom*self.N_unique_timepoints + 1,self.N_unique_timepoints)]
        
        return self.data        
    
    
    def to_a_csv(self, path, one_per_multi_c=False):
        '''
        Returns the data as a pandas dataframe with times as indexes 				
        
        :param path: String of path to store output
        :param one_per_multi_c: Boolean, if 'True' one measurement per dataframe will be exported otherwise all will be exported in one file. 
        '''
        for i in range(self.multi_chrom):
				self.data.to_csv(path + '_'  + str(i)) 
    
    def plot(self,titles=None,sharey=True,plot_multi=True):
        '''
        Plots the number the number of sample i.e. replicates/wells in the data 
        set. 
        
        :param titles: List-like object of subtitles 
        :param sharey: Boolean, default is True, where all y-axis limits will be identical. If False y-axis limits per plot are given by matplotlib defaults.
		:param plot_multi: Boolean, default is False, is several different measurements are present, only plot the first one. If False plots all of the values.      
        '''        
        if titles == None:
            titles = [None]*len(self.wells)
        
        
        nplots = len(self.rep) 
        rows =  int(np.ceil(nplots/5))
        fig = plt.figure(figsize=(15,rows*15),dpi=100,tight_layout=True)
        
        # Keeping track of the biggest range on y-axis 
        max_ylim = [10e6,0]  
 
        data = self.data
        
        if plot_multi == False:
			data = data.iloc[:self.N_unique_timepoints,:]
		
        for i in range(1,nplots):
            axes = fig.add_subplot(rows,5,i)
            iC = data.iloc[:, self.rep[i-1]:self.rep[i]]
            iC.plot(ax=axes,style='o', title=titles[i])
            
            if sharey: 
            
                low_y, high_y =  axes.get_ylim()
            
                if low_y < max_ylim[0] or high_y > max_ylim[1]:  
                    max_ylim[0], max_ylim[1] = min((max_ylim[0],low_y)), max((max_ylim[1],high_y))
                    for ax in fig.get_axes():
                        ax.set_ylim(tuple(max_ylim))
            
                axes.set_ylim(tuple(max_ylim))
                
		fig.show()


                

