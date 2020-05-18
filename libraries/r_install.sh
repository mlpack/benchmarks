#!/bin/bash
#
# Wrapper script to unpack and build R.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One R.tar.gz file should be located in this directory.
tars=`ls R.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source R.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf R/
mkdir R/
tar -xzpf R.tar.gz --strip-components=1 -C R/

cd R/
prefix_path="$(readlink -m ../)"

./configure --prefix=$prefix_path --enable-R-shlib
make
make install
cd ..
bin/Rscript install_r_packages.r
