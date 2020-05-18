#!/bin/bash
#
# Download each of the packages.
while read line;
do
  name=`echo $line | awk -F' ' '{ print $1 }'`;
  url=`echo $line | awk -F' ' '{ print $2 }'`;
  ext=${url##*.};
  if [ "$ext" == "gz" ]; then
    ext="tar.gz"; # Ugly hack.
  fi

  wget $url -O $name.$ext;

  if [ "$?" != "0" ]; then
    echo "Failure downloading $name!";
    exit 1;
  fi
done < package-urls.txt
