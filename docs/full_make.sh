#!/bin/bash

# !!! Only works on Unix-like Operating systems !!!

# full_make.sh

# Run to make at complete build of platelib. 
# REMEMBER to edit the version number in setup.py before running the script  

### Generates the documentation from source    

# generate modules files from python files 
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



