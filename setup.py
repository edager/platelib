#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 14:19:23 2018

@author: emil
"""

from setuptools import setup
from codecs import open

from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='platelib',
      version='0.1.5',
      description='Common tasks for working with platereader data',
      long_description=long_description,
	  long_description_content_type='text/markdown',
      author='Emil Dandanell Agerschou',
      author_email='bukser.med.slips@gmail.com',
      url='https://github.com/edager/platelib',
      license='LICENSE.txt',
      packages=['platelib'],
      classifiers=[
      	'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
		],
	  install_requires=[
		"xlrd >= 1.0",        
		"numpy >= 1.10",
        "pandas >= 0.19.0",
        "matplotlib >= 2.0.0",
		]
	 )

# Create source distributions by running: 
# python setup.py sdist 
