#!/bin/bash
#
# Wrapper script to unpack and build mprofiler.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One mprofiler.tar.gz file should be located in this directory.
tars='ls mprofiler.tar.gz | wc -l';
if [ "$tars" == "0" ];
then
  echo "No source mprofiler.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory
rm -rf mprofiler/
mkdir mprofiler/
tar -xzpf mprofiler.tar.gz --strip-components=1 -C mprofiler/

cd mprofiler/
python3 setup.py build
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
mkdir -p ../lib/$PYVER/site-packages/
PYTHONPATH=../lib/$PYVER/site-packages/ python3 setup.py install --prefix=../ -O2
