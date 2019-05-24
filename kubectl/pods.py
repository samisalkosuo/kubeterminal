
from .cmd import getNamespaces,getPods,describePod,logsPod,deletePod,getPodYaml,getPodJSON,execCmd,getPodLabels
from .nodes import getWorkerNodeNames

def delete(podName,namespaceName,force):
    return deletePod(podName,namespaceName,force)

def describe(podName,namespaceName,options):
    return describePod(podName,namespaceName,options)

def logs(podName,namespaceName,options):
    logText = logsPod(podName,namespaceName,options)
    return logText

def yaml(podName,namespaceName):
    return getPodYaml(podName,namespaceName)

def json(podName,namespaceName):
    return getPodJSON(podName,namespaceName)

def labels(podName,namespaceName):
    labelOutput = getPodLabels(podName,namespaceName)
    labelOutput = labelOutput.split("\n")[1].split()[5].split(",")
    labelOutput.sort()
    labelOutput = "\n".join(labelOutput)
    return labelOutput


def exec(podName,namespaceName,command):
    return execCmd(podName,namespaceName,command)

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
    return outputStr
