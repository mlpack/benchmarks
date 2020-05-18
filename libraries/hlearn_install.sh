#!/bin/bash
#
# Wrapper script to unpack and build HLearn.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One HLearn.tar.gz file should be located in this directory.  Also since
# HLearn depends on subhask, a subhask*.tar.gz file should also be located in
# this directory.
#
# HLearn doesn't work with ghc 8, so this installation is commented out.

#tars=`ls HLearn.tar.gz | wc -l`;
#if [ "$tars" == "0" ];
#then
#  echo "No source HLearn.tar.gz found in libraries/!"
#  exit 1
#fi

#subhasktars=`ls subhask.tar.gz | wc -l`;
#if [ "$tars" == "0" ];
#then
#  echo "No source subhask.tar.gz found in libraries/!"
#  exit 1
#fi

# Remove any old directory.
#rm -rf hlearn/
#mkdir hlearn/
#tar -xzpf HLearn.tar.gz --strip-components=1 -C hlearn/

#rm -rf subhask/
#mkdir subhask/
#tar -xvzpf subhask.tar.gz --strip-components=1 -C subhask/

#cd hlearn/
#cabal sandbox init
#cabal sandbox add-source ../subhask
#cabal update
#cabal install --only-dependencies --force-reinstalls
#cabal build
#cabal install
