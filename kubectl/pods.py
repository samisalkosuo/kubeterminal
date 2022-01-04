
from .cmd import getNamespaces,getPods
from .cmd import getPodLabels,getTop
from .nodes import getWorkerNodeNames


def labels(podName,namespaceName):
    labelOutput = getPodLabels(podName,namespaceName)
    labelOutput = labelOutput.split("\n")[1].split()[5].split(",")
    labelOutput.sort()
    labelOutput = "\n".join(labelOutput)
    return labelOutput

def top(podName,namespaceName,cmdString,isAllNamespaces=False,doAsciiGraph=False):
    output = getTop(podName,namespaceName,cmdString,isAllNamespaces)
    topOutput = output
    if doAsciiGraph == True:
        from ascii_graph import Pyasciigraph
        from ascii_graph.colors import Gre,Yel,Red
        from ascii_graph.colordata import vcolor
        from ascii_graph.colordata import hcolor

        graphSymbol='*'
        titleBarSymbol='-'
        graph = Pyasciigraph(titlebar=titleBarSymbol, graphsymbol=graphSymbol)

        output = ""
        #get data from top output
        cpuUsage = []
        memoryUsage = []
        cpuUsagePercentForNode = []
        memoryUsagePercentForNode = []
        lines = topOutput.split("\n")[1:]
        podName=None
        for line in lines:
            if(len(line)==0):
                continue
            fields=line.split()
            if cmdString.find("-c") > -1:
                podName=fields[0]
                cpuUse=(fields[1], int(fields[2].replace("m","")))
                memUse=(fields[1], int(fields[3].replace("Mi","")))
            elif cmdString.find("-n") > -1:
                #nodes, must be before isAllNamespaces check
                cpuUse=(fields[0], int(fields[1].replace("m","")))
                memUse=(fields[0], int(fields[3].replace("Mi","")))
                cpuUsagePercentForNode.append((fields[0], int(fields[2].replace("%",""))))
                memoryUsagePercentForNode.append((fields[0], int(fields[4].replace("%",""))))
            elif isAllNamespaces==True:
                rowTitle="%s/%s" % (fields[0],fields[1])
                cpuUse=(rowTitle, int(fields[2].replace("m","")))
                memUse=(rowTitle, int(fields[3].replace("Mi","")))
            else:
                cpuUse=(fields[0], int(fields[1].replace("m","")))
                memUse=(fields[0], int(fields[2].replace("Mi","")))
            cpuUsage.append(cpuUse)
            memoryUsage.append(memUse)

        cpuTitle='CPU (millicores)'
        if podName != None:
            cpuTitle="%s - %s" % (cpuTitle,podName)
        for line in  graph.graph(cpuTitle, cpuUsage):
            output = output + line + "\n"

        memTitle='Memory (Mi bytes)'
        if podName != None:
            memTitle="%s - %s" % (memTitle,podName)
        output= output + "\n"
        for line in  graph.graph(memTitle, memoryUsage):
           output = output + line + "\n"

        if cmdString.find("-n") > -1:
            #add percents for nodes
            pattern = [Gre, Yel, Red]
            # Color lines according to Thresholds
            thresholds = {
            0:  Gre, 50: Yel, 80: Red
            }
            data = hcolor(cpuUsagePercentForNode, thresholds)
            graph = Pyasciigraph(force_max_value=100, titlebar=titleBarSymbol, graphsymbol=graphSymbol)
            data = cpuUsagePercentForNode
            output= output + "\n"
            cpuTitle='CPU (%)'
            for line in  graph.graph(cpuTitle, data):
                output = output + line + "\n"

            output= output + "\n"
            memTitle='Memory (%)'
            for line in  graph.graph(memTitle, memoryUsagePercentForNode):
                output = output + line + "\n"

    return output

def list(namespace,nodehost=None):
    '''Return pods in namespace'''
    if nodehost == "all":
        nodehost=None

    nodeNames=None
    if nodehost == "workers":
        nodehost=None
        nodeNames = getWorkerNodeNames()
        #print(workerNodeNames)
        #kubectl get nodes -l node-role.kubernetes.io/worker=true
        #kubectl get pods --all-namespaces  --no-headers --field-selector spec.nodeName=10.31.10.126
        #return "\n".join(workerNodeNames)

    podsString=getPods(namespace,nodeNameList=nodeNames)
    podsString=podsString.strip()


    podsList=[]
    if nodehost != None:
        #get pods in given nodehost
        pods=podsString.split('\n')
        for pod in pods:
            if pod.find(nodehost)>-1:
                podsList.append(pod)

        #return "\n".join(podsList)
    else:
        podsList=podsString.split('\n')


    #sort list
    podsList.sort()

    #TODO: do not show pods in openshift-* namespaces
    # newPodsList = []
    # for pod in podsList:
    #     if pod.startswith("openshift-") == False:
    #         newPodsList.append(pod)
    # podsList = newPodsList

    podsListString = prettyPrint(podFieldsList(podsList),justify="L")
    #remove empty lines
    podsListString = "".join([s for s in podsListString.strip().splitlines(True) if s.strip()])
    return podsListString
#        return "\n".join(podsList)
        #return podsString

def podFieldsList(podsList):
    #return list of pod dictioaries
    #not used yet
    podsFieldsList=[]
    #pods=podsString.split('\n')
    for pod in podsList:
        podFieldList=[]
        fields=pod.split()
        podsFieldsList.append(fields)
        # if len(fields) == 8:
        #     #all namespaces
        #     podDict["namespace"]=fields[0]
        # singeNamespaceOffset=0
        # if len(fields) == 7:
        #     #single namespaces
        #     singeNamespaceOffset=1

        # podDict["name"] = fields[1-singeNamespaceOffset]
        # )
        # podDict["ready"] = fields[2-singeNamespaceOffset]
        # podDict["status"] = fields[3-singeNamespaceOffset]
        # podDict["restarts"] = fields[4-singeNamespaceOffset]
        # podDict["age"] = fields[5-singeNamespaceOffset]
        # podDict["pod_ip"] = fields[6-singeNamespaceOffset]
        # podDict["node_ip"] = fields[7-singeNamespaceOffset]

        # podsList.append(podDict)

    return podsFieldsList

# Pretty Print table in tabular format
# Original from: http://code.activestate.com/recipes/578801-pretty-print-table-in-tabular-format/
def prettyPrint(table, justify = "R", columnWidth = 0):
    
    try:        
        #get max column widths
        defaultColumnWidth=15 #15 is length of IP address
        def maxColumnWidth(columnIndex):
            columnWidth=0
            for row in table:
                width = len(str(row[columnIndex]))
                if width > columnWidth:
                    columnWidth = width
            return columnWidth

        #all column widths
        allWidths=[]
        try:
            for i in range(len(table[0])):
                allWidths.append(maxColumnWidth(i))
        except:
            #if table is empty string, this will be catched
            #and empty string is returned
            return ""


        outputStr = ""
        for row in table:
            rowList = []
            for i in range(len(row)):
                col = row[i]
            #for col in row:
                columnWidth = allWidths[i]
                if justify == "R": # justify right
                    rowList.append(str(col).rjust(columnWidth))
                elif justify == "L": # justify left
                    rowList.append(str(col).ljust(columnWidth))
                elif justify == "C": # justify center
                    rowList.append(str(col).center(columnWidth))
            outputStr += '  '.join(rowList) + "\n"
    except Exception as e:
        s = str(e)
        outputStr="%s\n%s" % (s,table)
    return outputStr
