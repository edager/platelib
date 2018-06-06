#!/usr/bin/env bash

# Run to push platelib source and docs to GitHub. 

# !!! Only works on Unix-like Operating systems !!!

# Before Running this:

	# Follow the instructions in BUILD.sh

	# Run BUILD.sh 

# commit and push
git add -A
git commit -m "building and pushing docs"
git push origin master

# switch branches and pull the data we want
git checkout gh-pages
rm -rf .
touch .nojekyll
git checkout master docs/build/html
mv ./docs/build/html/* ./
rm -rf ./docs
git add -A
git commit -m "publishing updated docs..."
git push origin gh-pages

# switch back
git checkout master
