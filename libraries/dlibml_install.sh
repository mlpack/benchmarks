#!/bin/bash
#
# Wrapper script to unpack and build dlibml.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One dlibml.tar.gz file should be located in this directory.

tars=`ls dlibml.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source dlibml.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf dlibml/
mkdir dlibml/
tar -xzpf dlibml.tar.gz --strip-components=1 -C dlibml/

cd dlibml/
mkdir build/
cd build/
cmake -DCMAKE_INSTALL_PREFIX=../../ ..
cmake --build . --config Release
make install
