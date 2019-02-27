from subprocess import check_output
import subprocess
import threading


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
    

def deletePod(podName,namespace):
    cmd="kubectl delete pod " + podName
    cmd=cmd +" -n "+namespace
    output = executeBackgroudCmd(cmd)
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