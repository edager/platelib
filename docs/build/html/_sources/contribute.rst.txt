Contribute
===========

Contributions are more than welcome, please raise an issue on the github page
highlighting the bug/extension/compatibilities before doing a pull request.

More tools
---------------
Apart from the tools listed in :ref:`Installation` the following is needed:   

	* Unix-like system
	* `git`_
	* `pandoc`_
 
.. _pandoc: https://pandoc.org/installing.html
.. _git: https://git-scm.com/downloads  


Building 
----------

You have made some wicked cool changes to the source code 
or the documentation that you want to share with the world, awesome! 

Now there's just a few steps before they can be incorporated into 
the platelib master branch

Changing the version number
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The versioning scheme of platelib should be done in reasonable 
accordance with the so called `Semantic versioning`_ where 
X.Y.Z should be read as MAJOR.MINOR.PATCH.    

The version number has to be changed in the two files ``setup.py`` and 
``docs/source/conf.py``

.. _Semantic versioning: https://semver.org/    

Create new source distribution 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Go to the docs folder and run::

	./full_make.sh	
 
If no errors occurred it can be uploaded to your local branch and 
a pull request can be made.


Planned improvements
--------------------- 

This is as much a wish-list as literally planned improvements: 


	* Plotting
		
		* Plotting of data from several plates in some sensible way.  

	* Fitting

		* Local fitting of traces in plate

		* Global fitting of traces in plate 
	
	* Statistical analysis    

		* Goodness-of-fit
		
		* Variance along traces, among replicates, and between conditions     

	* Python 3.X compatibility 
	* PyPI availability




   
