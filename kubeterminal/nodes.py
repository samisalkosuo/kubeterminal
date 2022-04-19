import re
from .cmd import getNodes, describeNode, getDescribeNodes

def describe(cmdOptions, selectedNode):
    node = ""
    options = cmdOptions.strip()
    if options == "":
        node = selectedNode
    else:
        node = options
    if node.find("all") > -1:
        return "Describing all nodes not (yet) implemented."
    return describeNode(node)
    
def getWorkerNodeNames():
    workerNodes = getNodes(noderole="worker")
    nodeNames = []
    for node in workerNodes.split("\n"):
        if node != "":
            nodeFields=node.split()
            nodeName=nodeFields[0]
            nodeNames.append(nodeName)
    return nodeNames

def describeNodes(noderole,params=[]):
    #describe nodes based on node role, for example: worker, master, proxy
    nodesDescribeText=getDescribeNodes(noderole)
    if "describe" in params:
        return nodesDescribeText

    startIndex=0
    endIndex=0
    singleNodeDescribeTexts=[]
    #get all node descriptions
    while endIndex>-1:
        startIndex=nodesDescribeText.find("Name:",endIndex)
        
        endIndex=nodesDescribeText.find("Name:",startIndex+1)
        if endIndex == -1:
            singleNodeDescribeTexts.append(nodesDescribeText[startIndex:])
        else:
            singleNodeDescribeTexts.append(nodesDescribeText[startIndex:endIndex])
    
    #loop through all nodes
    outputText=""
    cpuUsage=[]
    memoryUsage=[]
    #p = re.compile(r'^Name:\s+', re.M)
    for nodeDescription in singleNodeDescribeTexts:
        nameIndex=nodeDescription.find("Name:")
        nodeName=nodeDescription[6:nodeDescription.find("\n",nameIndex+6)]
        nodeName=nodeName.strip()
        ind=nodeDescription.find("Allocated resources:")
        allocatedResources=nodeDescription[ind:nodeDescription.find("Events:",ind)]
        ind=allocatedResources.find("cpu")
        cpu=allocatedResources[ind:allocatedResources.find("\n",ind)]
        cpu=re.sub(r'[a-zA-Z%()]', ' ', cpu)
        cpuUsage.append(cpu)
        ind=allocatedResources.find("memory")
        memory=allocatedResources[ind:allocatedResources.find("\n",ind)]
        memory=re.sub(r'[a-zA-Z%()]', ' ', memory)
        memoryUsage.append(memory)

        outputText=outputText+nodeName
        outputText=outputText+"\n"
        outputText=outputText+allocatedResources
        outputText=outputText+"\n"

    #total usage
    
    outputText=outputText+"\n"
    outputText=outputText+"Total CPU allocation (approx.):\n"
    outputText=outputText+getAllocatedResourcesString(cpuUsage)

    outputText=outputText+"\n"
    outputText=outputText+"Total memory allocation (approx.):\n"
    outputText=outputText+getAllocatedResourcesString(memoryUsage)

    return outputText

def getAllocatedResourcesString(usage):
    totalAllocation=0
    totalAllocatable=0
    for allocation in usage:
        alloc=allocation.split()
        usedCores=int(alloc[0].strip())
        totalAllocation=totalAllocation+usedCores
        used=int(alloc[1])/100.0
        totalAllocatable=totalAllocatable+int(usedCores/used)

    return "  %d%% (%d/%d)\n" % (int(100*totalAllocation/totalAllocatable),totalAllocation,totalAllocatable)

def list():
    '''Return list of tuples of nodes: [(value,label),(value,label),...]'''

    nodes = []
    nodesReady=0
    allNodes =  getNodes()
    for node in allNodes.split("\n"):
        if node != "":
            nodeFields=node.split()
            readyString=nodeFields[1]
            if readyString == "Ready":
                nodesReady=nodesReady+1
            value="%s %s %s %s" % (nodeFields[0],readyString,nodeFields[2],nodeFields[4])
            nodes.append((nodeFields[0],value))

    nodes.insert(0,("workers","all worker nodes"))
    nodes.insert(0,("all","all, ready %d/%d" % (nodesReady,len(nodes)-1) ))

    return nodes
    
