#!/bin/bash
#
# Wrapper script to unpack and build mlpack.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One mlpack.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.
tars=`ls mlpack.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No source mlpack.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf mlpack/
mkdir mlpack/
tar -xzpf mlpack.tar.gz --strip-components=1 -C mlpack/

cd mlpack/
mkdir build/
cd build/
cmake -DCMAKE_INSTALL_PREFIX=../../ -DBUILD_TESTS=OFF ../
make install

# Also install debug version.
cd ..
mkdir build-debug/
cd build-debug/
cmake -DDEBUG=ON -DCMAKE_INSTALL_PREFIX=../../debug/ -DBUILD_TEST=OFF ../
make install
