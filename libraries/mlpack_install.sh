#!/bin/bash
#
# Wrapper script to unpack and build mlpack.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One mlpack*.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.
tars=`ls mlpack*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No mlpack source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one mlpack source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf mlpack/
mkdir mlpack/
tar -xzpf mlpack*.tar.gz --strip-components=1 -C mlpack/

cd mlpack/
mkdir build/
cd build/
cmake -DCMAKE_INSTALL_PREFIX=../../ -DBUILD_TESTS=OFF ../
make install
