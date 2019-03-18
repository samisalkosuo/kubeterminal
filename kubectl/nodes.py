from .cmd import getNodes, describeNode

def describe(cmdOptions, selectedNode):
    node = ""
    options = cmdOptions.strip()
    if options == "":
        node = selectedNode
    else:
        node = options
    if node.find("all") > -1:
        return "Describing all nodes not (yet) supported."
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
    
