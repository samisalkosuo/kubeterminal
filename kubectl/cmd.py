from subprocess import check_output
import subprocess

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
    return output

def describePod(podName,namespace,options):
    cmd="kubectl describe pod " + podName
    cmd=cmd +" -n "+namespace +" "+ options
    output = executeCmd(cmd)
    return output

def logsPod(podName,namespace,options):
    cmd="kubectl logs " + podName
    cmd=cmd +" -n "+namespace +" "+options
    output = executeCmd(cmd)
    return output

def getNodes():
    cmd="kubectl get nodes "
    output = executeCmd(cmd+" --no-headers")
    return output

def describeNode(nodeName):
    cmd="kubectl describe node \"%s\" " % nodeName
    output = executeCmd(cmd)
    return output

def getPods(namespace):
    cmd="kubectl get pods "
    if namespace == "all-namespaces":
        cmd=cmd+"--"+namespace
    else:
        cmd=cmd+"-n "+namespace
    cmd=cmd+" -o wide "
    output = executeCmd(cmd+" --no-headers")
    return output

def getNamespaces():
    namespaces=[]
    output = executeCmd("kubectl get namespaces --no-headers")
    for line in output.split('\n'):
        fields = line.split()
        if len(fields) > 0:
            namespaces.append(fields[0])
    return namespaces