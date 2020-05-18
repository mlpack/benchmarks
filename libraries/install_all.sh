#!/bin/bash
#
# Install all of the packages, after removing whatever old packages were installed.
#
# The given argument is the number of cores to use for building (if applicable).
rm -rf bin/ lib/ share/ include/ debug/
mkdir bin/
mkdir lib/
mkdir share/
mkdir include/
mkdir debug/

./ann_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing ANN!";
  exit 1;
fi
./flann_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing FLANN!";
  exit 1;
fi
# HLearn is not supported on ghc 8. So it's commented out
#./hlearn_install.sh $1
#if [ "$?" != "0" ]; then
#  echo "Error installing HLearn!";
#  exit 1;
#fi
./matlab_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error checking for MATLAB!";
  exit 1;
fi
./mlpack_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing mlpack!";
  exit 1;
fi
./mlpy_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing mlpy!";
  exit 1;
fi
./scikit_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing scikit-learn!";
  exit 1;
fi
./nearpy_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing nearpy!";
  exit 1;
fi
./annoy_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing annoy!";
  exit 1;
fi
./shogun_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing shogun!";
  exit 1;
fi
./weka_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing Weka!";
  exit 1;
fi
./elki_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing ELKI!";
  exit 1;
fi
./mrpt_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing MRPT!";
  exit 1;
fi
./milk_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing Milk!";
  exit 1;
fi
./dlibml_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing dlib!";
  exit 1;
fi
./r_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing R!";
  exit 1;
fi
./dtimeout_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing dtimeout!";
  exit 1;
fi
./mprofiler_install.sh $1
if [ "$?" != "0" ]; then
  echo "Error installing mprofiler!";
  exit 1;
fi
