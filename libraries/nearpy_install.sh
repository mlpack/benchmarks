#!/bin/bash
#
# Wrapper script to unpack and build nearpy.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One Nearpy*.tar.gz file should be located in this directory.
tars=`ls nearpy.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No Nearpy source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" != "1" ];
then
  echo "More than one Nearpy source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf nearpy/
mkdir nearpy/
tar -xzpf nearpy.tar.gz --strip-components=1 -C nearpy/

cd nearpy/
python3 setup.py build
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
PYTHONPATH=../lib/$PYVER/site-packages/ python3 setup.py install --prefix=../ -O2
