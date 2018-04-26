Cookbook
=========


Reading in data
----------------
The main functionality of ``platelib`` is the ``read_plate`` function 
that allows for reading in platereader data from kinetic experiments
into a common framework namely into the ``Plate_data`` class.

It can be specified how many replicates per sample were prepared 
(default is ``3``)::

	p = read_plate('path/to/file', replicates=5)              

**NOTE that the number of replicates have to be the same for all samples!**

It can be specified which direction the replicates were loaded 
onto the plate where ``'hori'`` (horizontal) means towards 
increasing numbers and ``'vert'`` is towards increasing letters 
(default is ``'hori'``)::

	p = read_plate('path/to/file', rep_direction='vert')
  
**NOTE that the replicates have to be next to each other!**

Data from Tecan platereaders can be read in as (default is ``'bmg'``)::
	 
	p = read_plate('path/to/file', platereader='tecan')

**NOTE that this functionality has not been fully tested yet!**

As well as from BMG platereaders either where the data has prior
been transposed ``True`` such that well data are in column format     
or in row format ``False`` (default is ``True``)::

	p = read_plate('path/to/file', transposed=False)

The time unit can also be specified which as either ``'seconds'``, ``'minutes'``, ``'hours'``, or ``'days'`` will carry along into indexes
if exported and to unit of x-axis if plotted (default is ``'hours'``)::

	p = read_plate('path/to/file',time_unit='days')  

Accessing data
---------------
The ``Plate_data`` class allows for different ways of accessing the data

Through index:: 

	p[1]

Through index slice::

	p[::3]

Through well name::

	p['B02']  

Through list of well names:: 

	p[['B02','C03','D04']] 

Retrieved as a pandas.DataFrame with wellnames as column names and 
time points as index::

	df = Plate_data.to_a_dataframe()

Or as a (C)omma (S)eperated (V)aribles file with the first line
being (time unit + ) well names and the first column are the
time points::

    Plate_data.to_a_csv('path/to/file.csv')

Plotting data
-------------- 

The data is plotted according to replicates, and subtitles can be added (default is `None`),
and it can be specified whether all plots should have the same y-axis (default is `True`)::

	p.plot(titles=['condition 1', 'conditions 2'], sharey=False)

Will make the number of samples plots, all replicates of a given condition in the given plot. 

  
