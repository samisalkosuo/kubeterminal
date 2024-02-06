from subprocess import check_output
import subprocess
import threading
import locale
import os
from pubsub import pub
import base64
import binascii


def getKubeConfigFile():
    kubeconfigFile = os.environ.get("CURRENT_KUBECONFIG_FILE",None)
    if kubeconfigFile != None:
        return " --kubeconfig %s " % kubeconfigFile
    else:
        return ""

def getKubectlCommand():
    cmd = os.environ["KUBETERMINAL_CMD"]
    cmd = "%s %s" % (cmd, getKubeConfigFile())
    return cmd

#execute commands
def executeCmd(cmd,timeout=30):

    #TODO: if output is very long, this will hang until it is done
    output = ""
    try:
        output = check_output(cmd,shell=True,stderr=subprocess.STDOUT,timeout=timeout)
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
#    with open("output-file.txt", 'a') as out:
#      out.write(output + '\n')
    
    return output

#Thanks go to: http://sebastiandahlgren.se/2014/06/27/running-a-method-as-a-background-thread-in-python/
class ExecuteCommandBackground(object):
    def __init__(self, cmd, publishOutput = False,  publishTopic = 'print_output', decodeBase64 = False, decodeCert = False):
        self.cmd = cmd
        self.publishOutput = publishOutput
        self.publishTopic = publishTopic
        self.decodeBase64 = decodeBase64
        self.decodeCert = decodeCert
        if self.publishOutput == True:
            pub.sendMessage('background_processing_start',arg = self.cmd)
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        output = executeCmd(self.cmd)
        if self.decodeBase64 == True:
            output = output.replace("'","")
            try:
                #image_data = base64.b64decode(my_image_string, validate=True)
                output = base64.b64decode(output,validate = True)
                output = str(output,"utf8")
            except binascii.Error:
                #string is not base64
                pass
        if self.decodeCert == True:
            #output is assumed to be certificate and openssl tool is assumed to present
            try:
                import subprocess,os
                fName = ".cert.tmp"
                certFile = open(fName,"w")
                certFile.write(output)
                certFile.close()
                output = subprocess.check_output(["openssl", "x509", "-text", "-noout", 
                                        "-in", fName],stderr=subprocess.STDOUT,timeout=30)
                output = str(output,'utf-8')
                if os.path.exists(fName):
                    os.remove(fName)
            except Exception as e:
                #catch all errors
                output = str(e)

        if self.publishOutput == True:
            pub.sendMessage('background_processing_stop',arg = self.cmd)
            pub.sendMessage(self.publishTopic,arg = output, arg2 = self.cmd)


def executeBackgroudCmd(cmd):
    '''Execute command in background thread. Does not print output.'''
    ExecuteCommandBackground(cmd)
    return "Delete pod started in background. Refresh pod list to see status."       

def isAllNamespaceForbidden():
    output = executeCmd("%s get namespaces" % getKubectlCommand())
    return output.find("Forbidden") > -1

def isNodesForbidden():
    output = executeCmd("%s get nodes" % getKubectlCommand())
    return output.find("Forbidden") > -1

def deletePod(podName,namespace,force):
    cmd = getKubectlCommand() + " delete pod " + podName
    cmd=cmd + " -n " + namespace
    if (force == True):
        cmd=cmd + " --grace-period=0 --force"
    output = executeBackgroudCmd(cmd)
    return output

def getPodLabels(podName,namespace):
    resourceType = "pod"

    cmd = getKubectlCommand() + " get %s %s -n %s --show-labels" % (resourceType, podName, namespace)
    output = executeCmd(cmd)

    return output

def getTop(podName,namespace,cmdString,isAllNamespaces=False):
    cmd=None
    if cmdString.find("-c") > -1:
        #show top of selected pod and containers
        cmd = getKubectlCommand() + " top pod %s -n %s --containers" % (podName,namespace)

    if cmdString.find("-n") > -1:
        #show top of nodes
        cmd = getKubectlCommand() + " top nodes"

    if cmdString.find("-l") > -1:
        #show top of given labels
        label=cmdString.split()[2]
        cmd = getKubectlCommand() + " top pod  -n %s -l %s" % (namespace,label)

    if cmd == None:
        if isAllNamespaces==True:
            cmd = getKubectlCommand() + " top pods --all-namespaces"
        else:
            cmd = getKubectlCommand() + " top pods -n %s" % namespace
    
    output = executeCmd(cmd)

    return output


def execCmd(podName,namespace,command):
    cmd = getKubectlCommand() + " exec " + podName

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

def getLogs(podName,namespace,options):
    cmd = getKubectlCommand() + " logs " + podName
    cmd = cmd +" -n "+namespace +" "+options
    ExecuteCommandBackground(cmd, publishOutput = True,  publishTopic = 'print_logs')

def getNodes(noderole=None):
    cmd = getKubectlCommand() + " get nodes "
    if noderole != None:
       cmd = "%s -l node-role.kubernetes.io/%s" % (cmd,noderole)
    output = executeCmd(cmd+" --no-headers")
    return output

def describeNode(nodeName):
    cmd = getKubectlCommand() + " describe node \"%s\" " % nodeName
    output = executeCmd(cmd)
    return output

def getDescribeNodes(noderole=None):
    cmd = getKubectlCommand() + " describe nodes "
    if noderole != None:
       cmd = "%s -l node-role.kubernetes.io/%s" % (cmd,noderole)
    output = executeCmd(cmd)
    return output


def getPods(namespace,nodeNameList=[]):
    cmd = getKubectlCommand() + " get pods "

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
    #executeBackgroudCmd
    #executeCmd
    output = executeCmd(getKubectlCommand() + " get namespaces --no-headers",timeout=5)
    if output.find("namespaces is forbidden") > -1:
        #OpenShift does not allow normal users to list namespaces
        #OpenShift has resource project that can be used
        output = executeCmd(getKubectlCommand() + " get projects --no-headers")
        
    for line in output.split('\n'):
        fields = line.split()
        if len(fields) > 0:
            namespaces.append(fields[0])
    return namespaces

def getResources(resourceType, namespace):
    contentList=[]
    namespaceOption = " -n %s " % namespace
    allNamespaceOption = ""
    if namespace == "all-namespaces":
        namespaceOption = ""
        allNamespaceOption = "--all-namespaces"
    output = executeCmd(getKubectlCommand() + " %s get %s --no-headers %s" % (namespaceOption, resourceType, allNamespaceOption))
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    #    fields = line.split()
    #    if len(fields) > 0:
    #        services.append(fields[0])
    return contentList


def getContexts():
    contentList=[]
    output = executeCmd(getKubectlCommand() + " config get-contexts -o name")
    for line in output.split('\n'):
        if len(line.split()) > 0:
            contentList.append(line)
    return contentList

def getCurrentContext():
    contentList=[]
    output = executeCmd(getKubectlCommand() + " config current-context")
    return output.strip()

def listNamespaces():
    '''Return list of tuples of namespaces: [(value,label),(value,label),...]'''
    if isAllNamespaceForbidden() == True:
        namespaces = []
    else:
        namespaces = [("all-namespaces","All namespaces")]
    allNamespaces =  getNamespaces()
    
    for ns in allNamespaces:
        namespaces.append((ns,ns))

    return namespaces