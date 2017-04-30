#!/bin/bash
#
# This does not install MATLAB but instead simply checks for its presence.
if [ ! -f /opt/matlab/bin/matlab ];
then
  echo "MATLAB not found!"
  exit 1
fi
