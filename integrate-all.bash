#!/bin/bash

for city in  ${HOME}/cvprclg/data/train/*; do
  echo $city

  for dir in $city/*; do
    echo "  -$dir"
    local_dir=${dir##*/}
    mkdir -p $local_dir

    if [[ $local_dir == "geojson" ]]; then
      mkdir -p $local_dir/buildings
      for f in $dir/buildings/*; do
        ln -fs $f $local_dir/buildings/
      done
    else
      for f in $dir/*; do
        ln -s $f $local_dir/
      done
    fi
  done
done
