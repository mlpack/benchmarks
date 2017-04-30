#!/bin/bash
#
# Wrapper script to unpack and build ann.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One ann*.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.
tars=`ls ann*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No ann source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one ann source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf ann/
mkdir ann/
tar -xzpf ann*.tar.gz --strip-components=1 -C ann/

cd ann/
make linux-g++
cp -r include/* ../include/
cp -r bin/* ../bin/
cp -r lib/* ../lib/
