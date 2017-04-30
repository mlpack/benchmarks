#!/bin/bash
#
# Wrapper script to unpack and build weka.
#
# Include files will be installed to ../include/.
# Library files will be installed to ../lib/.
#
# One weka*.tar.gz file should be located in this directory.
tars=`ls scikit*.tar.gz | wc -l`;
if [ "$tars" -eq "0" ];
then
  echo "No weka source .tar.gz found in libraries/!"
  exit 1
fi
if [ "$tars" -ne "1" ];
then
  echo "More than one weka source .tar.gz found."
  echo "Ensure only one is present in libraries/!"
  exit 1
fi

# Remove any old directory.
rm -rf weka/
unzip weka*.zip
mv weka-[0-9]-[0-9]-[0-9]/ weka/

cd weka/
mkdir -p ../share/
cp weka.jar ../share/
