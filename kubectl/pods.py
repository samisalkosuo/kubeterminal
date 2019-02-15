
from .cmd import getNamespaces,getPods,describePod,logsPod

def describe(podName,namespaceName,options):
    return describePod(podName,namespaceName,options)

def logs(podName,namespaceName,options):
    logText = logsPod(podName,namespaceName,options)

    return logText

def list(namespace,nodehost=None):
    '''Return pods in namespace'''
    podsString=getPods(namespace)
    podsString=podsString.strip()
    if nodehost == "all":
        nodehost=None
        
    if nodehost != None:
        #get pods in given nodehost
        podsList=[]
        pods=podsString.split('\n')
        for pod in pods:
            if pod.find(nodehost)>-1:
                podsList.append(pod)
        return "\n".join(podsList)

    if 1 == 1:
        return podsString
    
    #not used yet
    podsList=[]
    pods=podsString.split('\n')
    for pod in pods:
        podDict=dict()
        fields=pod.split()
        if len(fields) > 4:
            if namespace == "all-namespaces":
                podDict["namespace"]=fields[0]
                podDict["name"]=fields[1]
                podDict["ready"]=fields[2]
                podDict["status"]=fields[3]
                podDict["restarts"]=fields[4]
                podDict["age"]=fields[5]
            else:
                podDict["name"]=fields[0]
                podDict["ready"]=fields[1]
                podDict["status"]=fields[2]
                podDict["restarts"]=fields[3]
                podDict["age"]=fields[4]
            podsList.append(podDict)
    
    return podsList
