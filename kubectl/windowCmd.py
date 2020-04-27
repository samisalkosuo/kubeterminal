#functions to get content for "pod"-window

from .pods import list as podList
from .cmd import getServices,getConfigMaps,getSecrets,getStatefulSets

def getPods(namespace, nodes):
    contentList=podList(namespace,nodes)
    podCount = len(contentList.split("\n"))
    title="%d Pods (ns: %s, nodes: %s)" % (podCount, namespace, nodes)
    return (contentList, title)

def getServiceList(namespace):
    contentList=getServices(namespace)
    podCount = len(contentList)
    title="%d Services (ns: %s)" % (podCount, namespace)
    return ("\n".join(contentList), title)

def getConfigMapList(namespace):
    contentList=getConfigMaps(namespace)
    podCount = len(contentList)
    title="%d ConfigMaps (ns: %s)" % (podCount, namespace)
    return ("\n".join(contentList), title)

def getSecretList(namespace):
    contentList=getSecrets(namespace)
    podCount = len(contentList)
    title="%d Secrets (ns: %s)" % (podCount, namespace)
    return ("\n".join(contentList), title)

def getStatefulSetList(namespace):
    contentList=getStatefulSets(namespace)
    podCount = len(contentList)
    title="%d StatefulSets (ns: %s)" % (podCount, namespace)
    return ("\n".join(contentList), title)
