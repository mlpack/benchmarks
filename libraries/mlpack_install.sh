#!/bin/bash
#
# Wrapper script to unpack and build mlpack.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One mlpack.tar.gz file should be located in this directory containing the
# source code of the desired mlpack version.  The first argument is the number
# of cores to use during build.
if [ "$1" == "" ]; then
  cores="1";
else
  cores="$1";
fi

tars=`ls mlpack.tar.gz | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source mlpack.tar.gz found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf mlpack/
mkdir mlpack/
tar -xzpf mlpack.tar.gz --strip-components=1 -C mlpack/

# Install mlpack
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
make -j$cores install

# Work around bug in 2.2.0 and 2.2.1.
cd ../../bin/
if [ ! -f mlpack_knn ]; then
  ln -s mlpack_knn mlpack_allknn
fi
if [ ! -f mlpack_kfn ]; then
  ln -s mlpack_kfn mlpack_allkfn
fi
if [ ! -f mlpack_krann ]; then
  ln -s mlpack_krann mlpack_allkrann
fi
cd ../debug/bin/
if [ ! -f mlpack_knn ]; then
  ln -s mlpack_knn mlpack_allknn
fi
if [ ! -f mlpack_kfn ]; then
  ln -s mlpack_kfn mlpack_allkfn
fi
if [ ! -f mlpack_krann ]; then
  ln -s mlpack_krann mlpack_allkrann
fi
