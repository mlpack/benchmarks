#!/bin/bash
#
# Wrapper script to unpack and build annoy.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One annoy.tar.gz file should be located in this directory.
tars=`ls annoy.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source annoy.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf annoy/
mkdir annoy/
tar -xzpf annoy.tar.gz --strip-components=1 -C annoy/

cd annoy/
python3 setup.py build
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
PYTHONPATH=../lib/$PYVER/site-packages/ python3 setup.py install --prefix=../ -O2
