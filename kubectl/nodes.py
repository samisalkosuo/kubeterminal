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

    nodes.insert(0,("all","all, ready %d/%d" % (nodesReady,len(nodes)) ))
    #return values for RadioList
    return nodes
    
    #return multiline string
    #return allNodes.strip()