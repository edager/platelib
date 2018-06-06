#!/usr/bin/env bash

# Run to make at complete build of platelib. 

# !!! Only works on Unix-like Operating systems !!!

# Before Running this:

	# Change the version number in setup.py and docs/source/conf.py 

	# Write meaningful commit messages in PUSH.sh 

### Generates the documentation from source    

# generate modules files from python files

cd docs/
 
sphinx-apidoc -f -o source/ ../platelib/ .

# generate html docs 
make clean html

# generate pdf docs
make latexpdf

cp build/latex/platelib-docs.pdf  platelib-docs.pdf

# generate README.md

pandoc -s source/introduction.rst source/install.rst source/cookbook.rst -o ../README.md

### Generate distributable

cd ..
python setup.py sdist  

