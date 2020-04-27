from subprocess import check_output
import subprocess
import threading
import locale


kubectlCommand = "kubectl"

#execute kubectl commands
def executeCmd(cmd):
    #TODO: if output is very long, this will hang until it is done
    output = ""
    try:
        output = check_output(cmd,shell=True,stderr=subprocess.STDOUT,timeout=30)
        output = output.decode('utf-8')
    except subprocess.CalledProcessError as E:
        output = E.output.decode('utf-8')
    except subprocess.TimeoutExpired as E:
        output = E.output.decode('utf-8')
        output = "TIMEOUT when executing %s\n\n%s" % (cmd, output)
    except:
        #catch all exception including decoding errors
        #assume decoding error
        system_encoding = locale.getpreferredencoding()
        output = output.decode(system_encoding)
        
    return output

def executeBackgroudCmd(cmd):
    '''Execute command in background thread. Does not print output.'''
    #Thanks go to: http://sebastiandahlgren.se/2014/06/27/running-a-method-as-a-background-thread-in-python/
    class BackgroundProcess(object):
        """ Background process  class
        The run() method will be started and it will run in the background
        """

        def __init__(self, cmd):
            self.cmd = cmd

            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True                            # Daemonize thread
            thread.start()                                  # Start the execution

        def run(self):
            output = ""
            try:
                output = check_output(self.cmd,shell=True,stderr=subprocess.STDOUT,timeout=30)
                output = output.decode('utf-8')
            except subprocess.CalledProcessError as E:
                output = E.output.decode('utf-8')
            except subprocess.TimeoutExpired as E:
                output = E.output.decode('utf-8')
                output = "TIMEOUT when executing %s\n\n%s" % (cmd, output)

    BackgroundProcess(cmd)
    return "Delete pod started in background. Refresh pod list to see status."       
    

def deletePod(podName,namespace,force):
    cmd = kubectlCommand + " delete pod " + podName
    cmd=cmd + " -n " + namespace
    if (force == True):
        cmd=cmd + " --grace-period=0 --force"
    output = executeBackgroudCmd(cmd)
    return output


def describePod(podName,namespace,options):
    cmd = kubectlCommand + " describe pod " + podName
    cmd=cmd +" -n "+namespace +" "+ options
    output = executeCmd(cmd)
    return output

def getPodYaml(podName,namespace):
    cmd = kubectlCommand + " get pod " + podName

    cmd=cmd+" -n " + namespace
    cmd=cmd+" -o yaml "
    output = ""
    output = executeCmd(cmd)

    return output

def getPodJSON(podName,namespace):
    cmd = kubectlCommand + " get pod " + podName

    cmd=cmd+" -n " + namespace
    cmd=cmd+" -o json "
    output = ""
    output = executeCmd(cmd)

    return output

def getPodLabels(podName,namespace):
    resourceType = "pod"

    cmd = kubectlCommand + " get %s %s -n %s --show-labels" % (resourceType, podName, namespace)
    output = executeCmd(cmd)

    return output

def getTop(podName,namespace,cmdString,isAllNamespaces=False):
    cmd=None
    if cmdString.find("-c") > -1:
        #show top of selected pod and containers
        cmd = kubectlCommand + " top pod %s -n %s --containers" % (podName,namespace)

    if cmdString.find("-n") > -1:
        #show top of nodes
        cmd = kubectlCommand + " top nodes"

    if cmdString.find("-l") > -1:
        #show top of given labels
        label=cmdString.split()[2]
        cmd = kubectlCommand + " top pod  -n %s -l %s" % (namespace,label)

    if cmd == None:
        if isAllNamespaces==True:
            cmd = kubectlCommand + " top pods --all-namespaces"
        else:
            cmd = kubectlCommand + " top pods -n %s" % namespace
    
    output = executeCmd(cmd)

    return output


def execCmd(podName,namespace,command):
    cmd = kubectlCommand + " exec " + podName

    cmd=cmd+" -n " + namespace
    if (command.find("-c")==0):
        #there is container
        commandList=command.split()
        #first is -c
        #second is container name
        containerName=commandList[1]
        cmd=cmd+" -c %s -- %s " % (containerName," ".join(commandList[2:]))
    else:
      cmd=cmd+" -- " + command
    output = executeCmd(cmd)

    return output



def logsPod(podName,namespace,options):
    cmd = kubectlCommand + " logs " + podName
    cmd=cmd +" -n "+namespace +" "+options
    output = executeCmd(cmd)
    return output

def getNodes(noderole=None):
    cmd = kubectlCommand + " get nodes "
    if noderole != None:
       cmd = "%s -l node-role.kubernetes.io/%s" % (cmd,noderole)
    output = executeCmd(cmd+" --no-headers")
    return output

def describeNode(nodeName):
    cmd = kubectlCommand + " describe node \"%s\" " % nodeName
    output = executeCmd(cmd)
    return output

def getDescribeNodes(noderole=None):
    cmd = kubectlCommand + " describe nodes "
    if noderole != None:
       cmd = "%s -l node-role.kubernetes.io/%s" % (cmd,noderole)
    output = executeCmd(cmd)
    return output


def getPods(namespace,nodeNameList=[]):
    cmd = kubectlCommand + " get pods "

    if namespace == "all-namespaces":
        cmd=cmd+"--"+namespace
    else:
        cmd=cmd+"-n "+namespace
    cmd=cmd+" -o wide "
    cmd=cmd+" --no-headers"
    output = ""
    if nodeNameList != None and len(nodeNameList)>0:
        #get pods for specified nodes
        for nodeName in nodeNameList:
            cmd2="%s --field-selector spec.nodeName=%s" % (cmd,nodeName)
            output2 = executeCmd(cmd2)
            if output2.lower().find("no resources found") == -1:
                output = output + output2
    else:
        output = executeCmd(cmd)

    return output

def getNamespaces():
    namespaces=[]
    output = executeCmd(kubectlCommand + " get namespaces --no-headers")
    for line in output.split('\n'):
        fields = line.split()
        if len(fields) > 0:
            namespaces.append(fields[0])
    return namespaces

def getServices(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get svc --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList

def getConfigMaps(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get cm --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList

def getSecrets(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get secrets --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList

def getStatefulSets(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get statefulset --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList

def getReplicaSets(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get replicaset --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList
    
def getDaemonSets(namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(kubectlCommand + " %s get daemonset --no-headers %s" % (namespaceOption,allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList