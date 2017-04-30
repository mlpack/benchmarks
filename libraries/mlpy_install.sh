#!/bin/bash
#
# Wrapper script to unpack and build mlpy.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One mlpy*.tar.gz file should be located in this directory.
tars=`ls mlpy*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No mlpy source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one mlpy source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf mlpy/
mkdir mlpy/
tar -xzpf mlpy*.tar.gz --strip-components=1 -C mlpy/

cd mlpy/
python3 setup.py build
python3 setup.py install --prefix=../../ -O2
