#!/bin/bash
#
# Wrapper script to unpack and build flann.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One flann*.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.
tars=`ls flann*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No flann source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one flann source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf flann/
mkdir flann/
tar -xzpf flann*.tar.gz --strip-components=1 -C flann/

cd flann/
mkdir build/
cd build/
cmake -DCMAKE_CXX_FLAGS=-I/usr/include/hdf5/serial/ \
    -DCMAKE_INSTALL_PREFIX=../../ \
    -DBUILD_PYTHON_BINDINGS=OFF \
    -DBUILD_MATLAB_BINDINGS=OFF \
    -DBUILD_CUDA_LIBRARY=OFF \
    ../
make install
