#!/bin/bash
#
# Install all of the packages.
./ann_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing ANN!";
  exit 1;
fi
./flann_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing FLANN!";
  exit 1;
fi
./hlearn_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing HLearn!";
  exit 1;
fi
./matlab_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error checking for MATLAB!";
  exit 1;
fi
./mlpack_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing mlpack!";
  exit 1;
fi
./mlpy_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing mlpy!";
  exit 1;
fi
./scikit_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing scikit-learn!";
  exit 1;
fi
./shogun_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing shogun!";
  exit 1;
fi
./weka_install.sh
if [ "$?" -ne "0" ]; then
  echo "Error installing Weka!";
  exit 1;
fi
