#!/bin/bash
#
# Wrapper script to unpack and build panns.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One panns.tar.gz file should be located in this directory.
tars=`ls panns.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No source panns.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf panns/
mkdir panns/
tar -xzpf panns.tar.gz --strip-components=1 -C panns/

cd panns/
python3 setup.py build
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
PYTHONPATH=../lib/$PYVER/site-packages/ python3 setup.py install --prefix=../ -O2
