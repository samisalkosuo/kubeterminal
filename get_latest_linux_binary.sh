#!/bin/bash

#__cmd could be podman
__cmd=docker

__tag=$1
if [[ "$__tag" == "" ]] ; then
  __tag=latest
fi

echo "Retrieving latest binary..."
${__cmd} create -it --name kubeterminal kazhar/kubeterminal:${__tag} bash
${__cmd} cp kubeterminal:/kubeterminal kubeterminal.bin
${__cmd} rm -fv kubeterminal
${__cmd} rmi kazhar/kubeterminal:${__tag}
echo "Latest binary downloaded as 'kubeterminal.bin'"
