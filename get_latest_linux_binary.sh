#!/bin/bash

__tag=$1
if [[ "$__tag" == "" ]] ; then
  __tag=latest
fi

echo "Retrieving latest binary..."
docker create -it --name kubeterminal kazhar/kubeterminal:${__tag} bash
docker cp kubeterminal:/kubeterminal kubeterminal.bin
docker rm -fv kubeterminal
docker rmi kazhar/kubeterminal:${__tag}
echo "Latest binary downloaded as 'kubeterminal.bin'"
