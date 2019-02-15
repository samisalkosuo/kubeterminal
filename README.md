# KubeTerminal

KubeTerminal is helper tool for Kubernetes.

The idea is to provide a tool that provides simple and quick tool to get the basics out of Kubernetes environment.

Features include (and more planned):

- Uses the shell and kubectl-command.
- List pods in namespace and/or node.
- See pod logs.
- Describe pods.
- Colors.

## Installation

## TODO

- refactor code
- make binary package that includes Python 3 runtime (for offline installations).
- add shell capability
- add Helm commands
- make customizable window layout
- add Kube services
- refactor code

## Screenshots

## Background

I'm working with Kubernetes quite a lot and I found that there a few basic commands that I use very, very often. For example:

- ```kubectl get pods```
- ```kubectl logs <pod name>```
- ```kubectl describe pod <pod name>```

Writing these commands take time, and when in hurry, that time is noticeable :-) 

I accidentally found [Kubebox](https://github.com/astefanutti/kubebox) and immediately tried it. 
But authentication failed when using IBM Cloud Private and self-signed certificate.

BTW, [IBM Cloud Private](https://www.ibm.com/cloud/private) is the main Kubernetes environment that I'm using ([there's free Community Edition available at Docker Hub](https://hub.docker.com/r/ibmcom/icp-inception/), you should try it :-).

Kubebox idea haunted until I remembered the existence of [Python Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) and rememberd that it can be used to create full-screen terminal application. Then I decided to make my own Kubebox, that I named KubeTerminal.
