#!/bin/bash
#
# Wrapper script to unpack and build shogun.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One shogun.tar.gz file should be located in this directory. The first argument
# is the number of cores to use for build.
if [ "$1" == "" ]; then
  cores="1";
else
  cores="$1";
fi

tars=`ls shogun.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source shogun.tar.gz found in libraries/!"
  exit 1
fi

gpl_tars=`ls shogun-gpl.tar.gz | wc -l`;
if [ "$gpl_tars" == "0" ];
then
    echo "No gpl source shogun-gpl.tar.gz found in libraries/!"
    exit 1
fi

# Remove any old directory.
rm -rf shogun/
mkdir shogun/
tar -xzpf shogun.tar.gz --strip-components=1 -C shogun/

# Add the gpl package
tar -xzpf shogun-gpl.tar.gz --strip-components=1 -C shogun/src/gpl

cd shogun/
mkdir build/
cd build/
PYVER=`python3 -c 'import sys; print("python" + sys.version[0:3])'`;
mkdir -p ../../lib/$PYVER/dist-packages/;
cmake -DPYTHON_INCLUDE_DIR=/usr/include/$PYVER \
    -DPYTHON_EXECUTABLE:FILEPATH=/usr/bin/python3 \
    -DPYTHON_PACKAGES_PATH=../../lib/$PYVER/dist-packages \
    -DINTERFACE_PYTHON=ON \
    -DBUILD_META_EXAMPLES=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_TESTING=OFF \
    -DCMAKE_INSTALL_PREFIX=../../ \
    ../
make
make install
