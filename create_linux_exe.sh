#!/usr/bin/bash

#this script create Linux executable to be used in offline installation.
#uses Docker to create the executable so there's no need to install any prereqs
#and non-Linux OS can be used to create Linux exe.

__name=kubeterminalbinary
__binary_file=kubeterminal.bin
docker build -t ${__name}  .
docker create -it --name ${__name} ${__name} bash
docker cp ${__name}:/root/dist/kubeterminal ${__binary_file}

echo "Linux executable: ${__binary_file}"
echo "Remember to chmod it."
