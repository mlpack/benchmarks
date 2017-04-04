#!/bin/bash
#
# Wrapper script to unpack and build HLearn.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One HLearn*.tar.gz file should be located in this directory.  Also since
# HLearn depends on subhask, a subhask*.tar.gz file should also be located in
# this directory.
tars=`ls HLearn*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No HLearn source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one HLearn source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

subhasktars=`ls subhask*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No subhask source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one subhask source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf hlearn/
mkdir hlearn/
tar -xzpf HLearn*.tar.gz --strip-components=1 -C hlearn/

rm -rf subhask/
mkdir subhask/
tar -xvzpf subhask*.tar.gz --strip-components=1 -C subhask/

cd hlearn/
cabal sandbox init
cabal sandbox add-source ../subhask
cabal update
cabal install --only-dependencies
cabal build
cabal install
