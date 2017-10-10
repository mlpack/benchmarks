#!/bin/bash
#
# Download and extract each dataset.
while read line;
do
  name=`echo $line | awk -F' ' '{ print $1 }'`;
  url=`echo $line | awk -F' ' '{ print $2 }'`;
  ext=${url##*.};
  if [ "$ext" == "gz" ]; then
    ext="tar.gz"; # Ugly hack.
  fi
  echo "$name"

  if [ -e "$name" ]; then
    echo "Skipping file: $name already exists."
  else
    name=${name/'*'};
    wget $url -O $name.$ext;

    if [ "$?" -ne "0" ]; then
      echo "Failure downloading $name!";
      exit 1;
    fi

    tar -xzpf $name.$ext
    rm $name.$ext
  fi
done < dataset-urls.txt
