#!/bin/bash
#
# Wrapper script to unpack and build ann.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One ann.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.  The first argument is the number
# of cores to use for build.
if [ "$1" == "" ]; then
  cores="1";
else
  cores="$1";
fi

tars=`ls ann.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source ann.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf ann/
mkdir ann/
tar -xzpf ann.tar.gz --strip-components=1 -C ann/

cd ann/
CXXFLAGS=-fPIC make -j$cores linux-g++
cp -r include/* ../include/
cp -r bin/* ../bin/
cp -r lib/* ../lib/
