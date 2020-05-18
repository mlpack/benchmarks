#!/bin/bash
#
# Wrapper script to unpack and build weka.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One weka.zip file should be located in this directory.
tars=`ls weka.zip | wc -l`;
if [ "$tars" == "0" ];
then
  echo "No source weka.zip found in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf weka/
unzip weka.zip
mv weka-[0-9]-[0-9]-[0-9]/ weka/

cd weka/
mkdir -p ../share/
cp weka.jar ../share/
