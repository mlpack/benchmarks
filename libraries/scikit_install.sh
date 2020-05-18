#!/bin/bash
#
# Wrapper script to unpack and build scikit.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One scikit.tar.gz file should be located in this directory.
tars=`ls scikit.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source scikit.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf scikit/
mkdir scikit/
tar -xzpf scikit.tar.gz --strip-components=1 -C scikit/

cd scikit/
python3 setup.py build
python3 setup.py install --prefix=../ -O2
