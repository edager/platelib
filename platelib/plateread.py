from __future__ import division 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from string import ascii_uppercase as A_up
from xlrd import open_workbook
 
# TODO:
# 1. Extract metadata/header from data files
# 2. Clean this function by turning the time conversion and reordering into seperate functions    
def read_plate(filename,replicates=3,rep_direction='hori',time_unit='hours',named_samples=[], 
               platereader='bmg',transposed=True):
    '''
    Reads in data from a CSV file from a BMG or Tecan platereader and returns a platedata object.
    
    :param filename:String, path to filename
    :param replicates: Positive integer, The number of replicates per sample.
    :param rep_direction: String, directions replicates is in. Only 'hori' and 'vert' are accepted directions where 'hori' if replicates are going from left to rigth 'vert' from replicates going from top to bottom. 
    :param time_unit: String, time unit one would like to have, accepted values are: 'seconds','minutes','hours','days'  
    :param named_samples: List of lists,  where each list should correpond to a sample and contain all replicates of it 
    :param platereader: String, The plate reader used to collect the data. Only 'bmg' and 'tecan' are accepted platereaders
    :param transposed: Bool, specifies wether the wells are in column (True) or row format (False).   
    '''
    if filename.lower().endswith(('.xls','.xlsx','.csv')) != True:
        raise ValueError('"{}" is not a supported filetype, only ".xls",".xlsx", and ".csv" are'.format(filename))

    if rep_direction not in ('vert','hori'):
        raise ValueError('"{}" is not a valid direction, only "vert" and "hori" are'.format(rep_direction)) 
    
    if type(named_samples) != list:
        raise TypeError('Expected a "list" for named_samples got a "{}"'.format(type(named_samples)))  

    if platereader not in ('bmg','tecan'):
        raise ValueError('"{}" platereader format is not supported , only "bmg" and "tecan" are'.format(platereader))
    
    if platereader == 'bmg': 
        if transposed:
            df = read_transposed_bmg(filename)
        else:
            df = read_untransposed_bmg(filename)

    else:   
        df = read_tecan(filename)
       
    # convert to specfied time units:
    df = to_time_units(df,time_unit)      

    # how many measurements at each time-point?
    multi_chrom = len(df.index.unique()) // len(df.index)
    
    replicates = range(0,len(df.columns)+replicates,replicates)	
    
    # reorder according to named samples   
    if len(named_samples) != 0:
        df, replicates = named_order(named_samples, df) 
    
    elif rep_direction=='vert':
        df = vert_order(replicates,df)
    
    return Plate_data(df, replicates, multi_chrom)


def search_start(filename):
    '''
    Find start of data region and returns the line number by finding the line that starts with "Well".
    
    :param filename: String, path to filename.   
    ''' 
    if filename.lower().endswith(('.xls','.xlsx')):
        wb = open_workbook(filename)
        s = wb.sheets()[0]
        for r in range(s.nrows):
                if s.cell(r,0).value == 'Well':
                    return r + 1
    
    else:
        with open(filename, 'r') as f:
            for r,line in enumerate(f):
                if line.startswith('Well'):
                    return r + 1                 


def read_transposed_bmg(filename):
    '''
    Reads in transposed data from a BMG platereader and returns a pandas DataFrame object.
    
    :param filename: String, path to filename.    
    '''
    start = search_start(filename) 
    skiprows = list(range(start - 1))
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
    
    :param filename: String, path to filename.   
    '''   
    skiprows = list(range(search_start(filename)))
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
    
    :param filename: String, path to filename   
    '''
    raw_d = pd.read_excel(filename, skiprows=list(range(62)), skipfooter=3,header=None)
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
def vert_order(replicates,df):
    '''
    Reorder dataframe column to vertical order, returns dataframe.
    
    :param replicates: List of positive integer number of replicates.  
    :param df: Pandas DataFrame 
    '''
    new_col_order = []
    diff = replicates[1]-replicates[0]   
    cols = df.columns.values
    for a in cols:
        # well already there ?
        if a not in new_col_order:
            # appends the well and replicates number of the wells below it 
            for i in [b+a[1:] for b in A_up[A_up.index(a[0]):A_up.index(a[0])+diff]]:
                new_col_order.append(i)
    return df[new_col_order]             


def named_order(named_samples, df):
    '''
    Reorder dataframe columns according to the specified order, returns dataframe and list of replicates.
    
    :param named_samples: List of lists, one list per samples containing all replicates
    :param df: Pandas DataFrame  
    '''
    rep_per_sample = [len(i) for i in named_samples]
    rep_per_sample.insert(0,0)
    replicates = np.cumsum(rep_per_sample)
    return df[[n for sample in named_samples for n in sample]], replicates


def to_time_units(df,time_unit):
    '''
    Convert the index a dataframe into the time unit specified, returns dataframe.
    
    :param df: Pandas DataFrame
    :param time_unit: String, allowed values are 'seconds' ,'minutes','hours', and 'days'.  
    '''    
    Timepars = {'seconds':1.0,'minutes':60.0,'hours':3600.0,'days':86400.0}
    try:
        df.index = df.index/Timepars[time_unit]
        return df
    except KeyError:
        raise ValueError('"{}" is not a valid time_unit, only "seconds", "minutes", "hours", and "days" are'.format(time_unit))
            
            
class Plate_data():
    '''
    Class for containing data from a platereader assay. 

    :param data: Pandas DataFrame with time points as index and wells as columns
    :param replicates: Positive integer of replicates, assuming equal number of replicates of all samples     
    '''
    def __init__(self, data, replicates, multi_chrom):
        self.data = data
        self.multi_chrom = multi_chrom
        self.rep = replicates   
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
            raise TypeError("Invalid argument type.")
    
    # returns the number of columns i.e. wells        
    def __len__(self):
        return len(self.wells)


    def to_a_dataframe(self, one_per_multi_c=False):
        '''
        Returns the data as a list of pandas dataframe(s) with times as indexes 				
        
        :param one_per_multi_c: Bool, if 'True' one measurement per dataframe will be exported, if False all will be exported in one dataframe.              
        '''
        if one_per_multi_c: 
            N = self.N_unique_timepoints
            m = self.multi_chrom
            return [self.data.iloc[i-N:i] for i in range(0,m*N + 1,N)]
        
        return self.data        
    
    
    def to_a_csv(self, path, one_per_multi_c=False):
        '''
        Returns the data as a pandas dataframe with times as indexes 				
        
        :param path: String of path to store output
        :param one_per_multi_c: Bool, if 'True' one measurement per dataframe will be exported otherwise all will be exported in one file. 
        '''
        for i in range(self.multi_chrom):
            self.data.to_csv(path + '_'  + str(i)) 
            
    
    def plot(self,titles=None,sharey=True,plot_multi=True,return_fig=False):
        '''
        Plots the number of samples i.e. replicates/wells in the data set. 
        
        :param titles: List-like object of subtitles 
        :param sharey: Bool, if True all y-axis limits will be identical, if False y-axis limits are given by matplotlib defaults.
        :param plot_multi: Bool, if several different measurements are present per time point, only plot the first one, if False plots all of the values.      
        :param return_fig: Bool, if True returns a figure object, if False only plot the data 
        '''        
        data = self.data
        nplots = len(self.rep)  - 1
        rows =  int(np.ceil(nplots/5))   
    
        if titles == None:
            titles = [None]*nplots
        
        if not plot_multi:
                data = data.iloc[:self.N_unique_timepoints,:]

        fig, axes= plt.subplots(nrows=rows,ncols=5,sharey=sharey,
                                figsize=(15,rows*15), dpi=100, tight_layout=True)

        for i, ax in zip(range(nplots), axes.flat):
            iC = data.iloc[:, self.rep[i]:self.rep[i+1]]
            iC.plot(ax=ax,style='o', title=titles[i])
               
        # Remove empty plots:
        for j in range(nplots,len(axes.flat)):
           fig.delaxes(axes.flatten()[j])     
        
        fig.show()
        
        if return_fig:
            return fig
                

def add_lines(fig, hori=False, vert=False):
    '''
    Adds horizontal and figure lines to each plot in a subplot
    
    :param fig: matplotlib figure object
    :param hori: Float, y position where the horizontal will be at 
    :param vert: Float, x position where the horizontal will be at   
    '''    
    for ax in fig.axes:    
        if hori:
            xmin,xmax = ax.get_xlim()
            ax.hlines(hori,xmin=xmin,xmax=xmax,linewidth=2, linestyle='--')
        
        if vert:
            ymin,ymax = ax.get_ylim()
            ax.set_ylim((ymin,ymax))
            ax.vlines(vert,ymin=ymin,ymax=ymax,linewidth=2, linestyle='--')

    