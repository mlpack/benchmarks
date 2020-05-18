#!/bin/bash
#
# Wrapper script to unpack and build milk.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One milk.tar.gz file should be located in this directory.
tars=`ls milk.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source milk.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf milk/
mkdir milk/
tar -xzpf milk.tar.gz --strip-components=1 -C milk/

cd milk/
python3 setup.py build
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
PYTHONPATH=../lib/$PYVER/site-packages/ python3 setup.py install --prefix=../ -O2
