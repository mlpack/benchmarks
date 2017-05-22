#!/bin/bash
#
# Wrapper script to unpack and build shogun.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One shogun.tar.gz file should be located in this directory. The first argument
# is the number of cores to use for build.
if [ "$1" -eq "" ]; then
  cores="1";
else
  cores="$1";
fi

tars=`ls shogun.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No source shogun.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf shogun/
mkdir shogun/
tar -xzpf shogun.tar.gz --strip-components=1 -C shogun/

cd shogun/
mkdir build/
cd build/
cmake -DPYTHON_INCLUDE_DIR=/usr/include/python3.5 \
    -DPYTHON_EXECUTABLE:FILEPATH=/usr/bin/python3 \
    -DPYTHON_PACKAGES_PATH=../../lib/python3.5/dist-packages \
    -DPythonModular=ON \
    -DBUILD_META_EXAMPLES=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTING=OFF \
    -DCMAKE_INSTALL_PREFIX=../../ \
    ../
make -j$cores
make install
