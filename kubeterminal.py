import datetime
import base64
import re
import argparse 
import os

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit,VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit.widgets import SystemToolbar
from prompt_toolkit.widgets import Frame, RadioList, VerticalLine, HorizontalLine, TextArea
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.keys import Keys
from prompt_toolkit import eventloop
from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.utils import Event
from prompt_toolkit.filters import to_filter

#set command before importing 
os.environ["KUBETERMINAL_CMD"] = "kubectl"

from kubectl import namespaces,pods,nodes,windowCmd
from application import state,lexer
from kubectl import cmd 
from application import globals
from kubectl import permissions

#CLI args
parser = argparse.ArgumentParser()
parser.add_argument('--no-dynamic-title', action="store_true", help='Do not set command window title to show NS, node and pod.')
parser.add_argument('--compact-windows', action="store_true", help='Set namespace, node and pod windows to more compact size.')
parser.add_argument('--even-more-compact-windows', action="store_true", help='Set namespace, node and pod windows to even more compact size.')
parser.add_argument('--oc', action="store_true", help='Use oc-command insteand of kubectl.')
parser.add_argument('--no-help', action="store_true", help='Do not show help when starting KubeTerminals.')
args = parser.parse_args()

if args.oc == True:
    os.environ["KUBETERMINAL_CMD"] = "oc"

helpText = """KubeTerminal

Helper tool for Kubernetes.

This output window shows output of commands.
"Selected pod/resource" is the resource where cursor is in the Resources window.

Key bindings

- ESC - exit program.
- <alt-1>, show pods.
- <alt-2>, show configmaps.
- <alt-3>, show services.
- <alt-4>, show secrets.
- <alt-5>, show statefulsets.
- <alt-6>, show replicasets.
- <alt-7>, show daemonsets.
- <alt-8>, show persistentvolumeclaims.
- <alt-9>, show persistentvolumes.
- <alt-10>, show deployments.
- <alt-11>, show storageclasses.
- <alt-12>, show jobs.
- <alt-13>, show cronjobs.
- <alt-14>, show roles.
- <alt-15>, show rolebindings.
- <alt-16>, show serviceaccounts.
- <alt-17>, show poddisruptionbudgets.
- <alt-18>, show routes.
- <alt-19>, show ingresses.
- <alt-20>, show nodes.
- <alt-21>, show customresourcedefinitions.
- <alt-22>, show namespaces.
- <ctrl-l>, show logs of currently selected pod (without any options).
- <ctrl-d>, show description of currently selected resource (without any options).
- <ctrl-y>, show YAML of currently selected resource.
- <ctrl-r>, refresh resource (pod etc.) list.
- <shift-g>, to the end of Output-window buffer.
- <shift-w>, toggle wrapping in Output-window.
- / -  search string in Output-window.

Commands:

- help - this help.
- cert <data key> - show certificate of secret value using openssl.
- clip - copy Output-window contents to clipboard.
- cls - clear Output-window.
- contexts - show current and available contexts.
- decode <data key> - decode base64 encoded secret or configmap value.
- delete [--force] - delete currently selected pod, optionally force delete.
- describe <describe options> - show description of currently selected resource.
- exec [-c <container_name>] <command> - exec command in currently selected pod.
- json - get JSON of currently selected resource.
- ku <cmds/opts/args> - execute kubectl in currently selected namespace.
- labels - show labels of currently selected pod.
- logs [-c <container_name>] - show logs of currently selected pod.
- oc <cmds/opts/args> - execute oc in currently selected namespace.
- save [<filename>] - save Output-window contents to a file.
- shell <any shell command> - executes any shell command.
- top [-c | -l <label=value> | -n | -g] - show top of pods/containers/labels/nodes. Use -g to show graphics.
- window [<window name> | list] - Set resource type for window. 'window list' lists available windows.
- workers [-d] - get worker node resource allocation. Use -d to describe all worker nodes.
- wrap - toggle wrapping in Output-window.
- yaml - get YAML of currently selected resource.

"""


applicationState = state#state.State()

applicationState.content_mode=globals.WINDOW_POD

namespaceWindowSize=27
nodeWindowSize=53
podListWindowSize=80
if args.compact_windows == True:
    namespaceWindowSize=20
    nodeWindowSize=30
    podListWindowSize=50
if args.even_more_compact_windows == True:
    namespaceWindowSize=20
    nodeWindowSize=10
    podListWindowSize=30
if permissions.isForbiddenNodes() == True:
    namespaceWindowSize=80


enableMouseSupport = False
enableScrollbar = False

#TODO: refactor code, all code

def updateState():
    
    selected_namespace=namespaceWindow.current_value
    selected_node=nodeListArea.current_value
    selected_pod=str(podListArea.buffer.document.current_line).strip()

    if applicationState.selected_pod != selected_pod:
        #somethingSelected=applicationState.selected_pod
        applicationState.selected_pod = selected_pod
        #f somethingSelected != "":
        #    updateUI("selectedpod")

    if applicationState.current_namespace != selected_namespace:
        applicationState.current_namespace = selected_namespace
        #reset position
        state.cursor_line = -1

        updateUI("namespacepods")

    if applicationState.selected_node != selected_node:
        applicationState.selected_node = selected_node
        #reset position
        state.cursor_line = -1

        updateUI("nodepods")

def updateUI(updateArea):
    
    if updateArea == "selectedpod":
        appendToOutput(applicationState.selected_pod)

    if updateArea == "nodepods" or updateArea == "namespacepods":
        moveToLine=state.cursor_line
        ns = applicationState.current_namespace
        contentList = ""
        title = ""
        (contentList,title) = windowCmd.getWindowContentAndTitle(applicationState.content_mode, ns,applicationState.selected_node)
                
        podListArea.text=contentList
        podListAreaFrame.title=title
        setCommandWindowTitle()
        if moveToLine > 0:
            #if pod window cursor line was greater than 0 
            #then move to that line
            #appendToOutput("Should move to line: %d" % moveToLine)
            podListArea.buffer.cursor_down(moveToLine)


kb = KeyBindings()
# Global key bindings.

@kb.add('tab')
def tab_(event):
    updateState()
    #refresh UI
    focus_next(event)

@kb.add('s-tab')
def stab_(event):
    updateState()
    #refresh UI
    focus_previous(event)

@kb.add('escape')
def exit_(event):
    """
    Pressing Esc will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `CommandLineInterface.run()` call.
    """
    event.app.exit()

@kb.add('c-d')
def describepod_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("describe")

@kb.add('c-y')
def yamlResource_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("yaml")

@kb.add('c-l')
def logspod_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("logs")

@kb.add('c-r')
def logspod_(event):
    #refresh pods
    updateState()
    updateUI("namespacepods")

@kb.add('G')
def toendofoutputbuffer_(event):    
    outputArea.buffer.cursor_down(outputArea.document.line_count)

@kb.add('W')
def togglewrap_(event):    
    toggleWrap()

@kb.add('c-u')
def _(event):
    executeCommand("use-context")

@kb.add('c-up')
def _(event):
    executeCommand("use-context")

@kb.add('escape','down')
def _(event):
    executeCommand("window")


def changeWindow(windowName):
    updateState()
    executeCommand("window %s" % windowName)

#change window keyboard shortcuts
@kb.add('escape','w')
def _(event):
    executeCommand("window")
    #print('Control-A pressed, followed by Control-B')

@kb.add('escape','0')
def _(event):
    appendToOutput("No window",cmdString="Alt-0")

@kb.add('escape','1')
def _(event):
    changeWindow("pod")

@kb.add('escape','2')
def _(event):
    changeWindow("svc")

@kb.add('escape','3')
def _(event):
    changeWindow("cm")

@kb.add('escape','4')
def _(event):
    changeWindow("secret")

@kb.add('escape','5')
def _(event):
    changeWindow("sf")

@kb.add('escape','6')
def _(event):
    changeWindow("rs")

@kb.add('escape','7')
def _(event):
    changeWindow("ds")

@kb.add('escape','8')
def _(event):
    changeWindow("pvc")

@kb.add('escape','9')
def _(event):
    changeWindow("pv")

@kb.add('escape','1','escape','0')
def _(event):
    changeWindow("deployment")

@kb.add('escape','1','escape','1')
def _(event):
    changeWindow("sc")

@kb.add('escape','1','escape','2')
def _(event):
    changeWindow("job")

@kb.add('escape','1','escape','3')
def _(event):
    changeWindow("cronjob")

@kb.add('escape','1','escape','4')
def _(event):
    changeWindow("role")

@kb.add('escape','1','escape','5')
def _(event):
    changeWindow("rolebinding")

@kb.add('escape','1','escape','6')
def _(event):
    changeWindow("sa")

@kb.add('escape','1','escape','7')
def _(event):
    changeWindow("pdb")

@kb.add('escape','1','escape','8')
def _(event):
    changeWindow("route")


@kb.add('escape','1','escape','9')
def _(event):
    changeWindow("ingress")

@kb.add('escape','2','escape','0')
def _(event):
    changeWindow("node")

@kb.add('escape','2','escape','1')
def _(event):
    changeWindow("crd")

@kb.add('escape','2','escape','2')
def _(event):
    changeWindow("namespace")

#search keyboard
@kb.add('/')
def searchbuffer_(event):
    #search both pods and output window at the same time
    if (len(command_container.text)>0):
        #if length of text is command container is > 0
        # assume that command is currently written
        #ignore search
        command_container.text=command_container.text+"/"
        command_container.buffer.cursor_right(len(command_container.text))
        
        return
    
    layout.focus(command_container)
    command_container.text="/"
    command_container.buffer.cursor_right()


#content windows
namespaceList = namespaces.list()
nodesList = nodes.list()

namespaceWindow = RadioList(namespaceList)
windowHeight = len(namespaceList) + 2 
if windowHeight > 8:
    windowHeight = 8
namespaceWindowFrame= Frame(namespaceWindow,title="Namespaces",height=windowHeight,width=namespaceWindowSize)

nodeListArea = RadioList(nodesList)
nodeWindowFrame= Frame(nodeListArea,title="Nodes",height=windowHeight,width=nodeWindowSize)
#check permissions for nodes
#normal OpenShift user does not see nodes nor namespaces other than his/her own.
if permissions.isForbiddenNodes() == True:
    #if user can not see Nodes do not show node window
    upper_left_container = namespaceWindowFrame
else:
    upper_left_container = VSplit([namespaceWindowFrame, 
                #HorizontalLine(),
                #Window(height=1, char='-'),
                nodeWindowFrame])


def setCommandWindowTitle():
    selected_namespace=namespaceWindow.current_value
    selected_node=nodeListArea.current_value
    selected_pod=str(podListArea.buffer.document.current_line).strip()

    if selected_namespace == "all-namespaces":
        fields = selected_pod.split()
        selected_namespace = fields[0]
        selected_pod = " ".join(fields[1:])
    title = ""
    title = windowCmd.getCommandWindowTitle(applicationState.content_mode, selected_namespace, selected_node, selected_pod)

    if applicationState.content_mode == globals.WINDOW_CONTEXT:
        #select current context as title
        selected_pod = str(podListArea.buffer.document.current_line).strip()
        title = "Context: %s" % (selected_pod)
        #title = "Current Context: %s" % (applicationState.current_context)

    title = title.replace("<none>", '')
    title = re.sub(' +', ' ', title)
    commandWindowFrame.title = title

#listens cursor changes in pods list
def podListCursorChanged(buffer):
    #when position changes, save cursor position to state
    state.cursor_line = buffer.document.cursor_position_row

    if args.no_dynamic_title == False:
        setCommandWindowTitle()

#pods window
podListArea = TextArea(text="", 
                multiline=True,
                wrap_lines=False,
                scrollbar=enableScrollbar,
                lexer=lexer.PodStatusLexer(),
                read_only=True                
                )

#add listener to cursor position changed
podListArea.buffer.on_cursor_position_changed=Event(podListArea.buffer,podListCursorChanged)
podListArea.window.cursorline = to_filter(True)
podListAreaFrame = Frame(podListArea,title="Pods",width=podListWindowSize)

left_container = HSplit([upper_left_container, 
                #HorizontalLine(),
                #Window(height=1, char='-'),
                podListAreaFrame])

#print(namespaceWindow.current_value)
#output area to output debug etc stuff
outputArea = TextArea(text="", 
                    multiline=True,
                    wrap_lines=False,
                    lexer=lexer.OutputAreaLexer(),
                    scrollbar=enableScrollbar,
                    read_only=True)
outputAreaFrame= Frame(outputArea,title="Output")

content_container = VSplit([
    # One window that holds the BufferControl with the default buffer on
    # the left.
    left_container,
    # A vertical line in the middle. We explicitly specify the width, to
    # make sure that the layout engine will not try to divide the whole
    # width by three for all these windows. The window will simply fill its
    # content by repeating this character.
    #VerticalLine(),
    #Window(width=1, char='|')
    
    # Display the text 'Hello world' on the right.
    #Window(content=FormattedTextControl(text='Hello world, Escape to Quit'))
    outputAreaFrame

])

def appendToOutput(text,cmdString="",overwrite=False):

    if text is None or "No resources found" in text:    
        return
    
    #TODO: option to set UTC or local
    #now = datetime.datetime.utcnow().isoformat()
    now = datetime.datetime.now().isoformat()
    if cmdString == "":
        header = "=== %s ===" % now
    else:
        header = "=== %s - %s ===" % (now,cmdString)
    
    if outputArea.text == "":        
        outputArea.text="\n".join([header,text,""])
    else:
        outputArea.text="\n".join([outputArea.text,header,text,""])
    
#    outputArea.buffer.cursor_position=len(outputArea.text)
    outputIndex=outputArea.text.find(header)
    outputArea.buffer.cursor_position=outputIndex#len(outputArea.text)
    outputArea.buffer.cursor_down(30)


def getShellCmd(namespace,cmdString):
    
    if cmdString.find("ku ") == 0 or cmdString.find("oc ") == 0:
        cmdName = "kubectl"
        if cmdString.find("oc ") == 0:
            cmdName = "oc"
        #command arguments af "oc" or "ku"
        cmdArgs = cmdString[2:].strip()
        #namespace argument added if not global resource like storageclass
        namespaceArg = ""
        if windowCmd.isGlobalResource(applicationState.content_mode) == False:
            namespaceArg = " -n %s" % namespace        
            
        cmdString  = "shell %s %s %s" % (cmdName, namespaceArg, cmdArgs)
    
    return cmdString


#command handler for shell
def commandHander(buffer):
    #check incoming command
    cmdString = buffer.text
    executeCommand(cmdString)


#actual command handler, can be called from other sources as well
def executeCommand(cmdString):
    import os#os imported also here because import at the beginning is not in this scope...
    refreshUIAfterCmd = False
    text=""
    cmdcmdString = cmdString.strip()
    if cmdString == "":
        return

    if cmdString == "help":
        text=helpText


    def getResourceNameAndNamespaceName():

        if applicationState.content_mode == globals.WINDOW_CONTEXT:
            return (applicationState.resource_namespace,applicationState.resource_resourceName)

        podLine = applicationState.selected_pod

        namespace=""
        resourceName=""
        if podLine != "":
            fields=podLine.split()

            #if resource is global like storage class, 
            #resource name is first field and there is no namespace
            if windowCmd.isGlobalResource(applicationState.content_mode) == True:
                resourceName=fields[0]
                namespace=""
            else:
                if applicationState.current_namespace == "all-namespaces":
                    resourceName=fields[1]
                    namespace=fields[0]
                else:
                    resourceName=fields[0]
                    namespace=applicationState.current_namespace
        
        return (namespace,resourceName)

    def isAllNamespaces():
        return applicationState.current_namespace == "all-namespaces"

    def getCmdString(cmd, resource):
        resourceType = windowCmd.getResourceType(applicationState.content_mode)
        
        if cmd == "describe":
            commandString ="ku describe %s %s" % (resourceType,resource)
        if cmd == "yaml":
            commandString ="ku get %s %s -o yaml" % (resourceType,resource)
        if cmd == "json":
            commandString ="ku get %s %s -o json" % (resourceType,resource)

        return commandString

    (namespace,resourceName)=getResourceNameAndNamespaceName()

    if cmdString.find("logs") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            if namespace!="" and resourceName != "":
                options=cmdString.replace("logs","")
                cmdString = "logs " + resourceName
                text=pods.logs(resourceName,namespace,options)                
                index = text.find("choose one of: [")
                if index > -1:
                    text1 = text[0:index]
                    text2 = text[index:]
                    text2 = text2.replace("choose one of: [","choose one of:\n[")
                    text = "%s\n%s" % (text1, text2)
        else:
            text = "ERROR: Logs are available only for pods."

    if cmdString.find("describe") == 0:
        cmdString = getCmdString("describe",resourceName)

    if cmdString.find("yaml") == 0:
        cmdString = getCmdString("yaml",resourceName)

    if cmdString.find("json") == 0:
        cmdString = getCmdString("json",resourceName)

    if cmdString.find("label") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            cmdString = "labels %s" % (resourceName)
            text=pods.labels(resourceName,namespace)
        else:
            text = "ERROR: Labels are currently available only for pods."

    if cmdString.find("decode") == 0:
        if applicationState.content_mode == globals.WINDOW_SECRET or applicationState.content_mode == globals.WINDOW_CM:
            cmdArgs = cmdString.split()
            if len(cmdArgs) > 1:
                key = cmdArgs[1]
                cmdString =""
                if applicationState.content_mode == globals.WINDOW_SECRET:
                    cmdString = "secret "
                if applicationState.content_mode == globals.WINDOW_CM:
                    cmdString = "cm "
                cmdString = "%s %s %s --decode " % (cmdString,resourceName, key)
            else:
                text = "ERROR: No key name given."
        else:
            text = "ERROR: Decode available only for secrets and configmaps."

    if cmdString.find("cert") == 0:
        if applicationState.content_mode == globals.WINDOW_SECRET:
            cmdArgs = cmdString.split()
            if len(cmdArgs) > 1:
                key = cmdArgs[1]
                cmdString = "secret %s %s --cert " % (resourceName, key)
            else:
                text = "ERROR: No key name given."
        else:
            text = "ERROR: cert available only for secrets."


    doBase64decode = False
    isCertificate = False
    #this command is used by decode and cert commands
    #these secret or cm commands not shown in help
    if cmdString.find("secret") == 0 or cmdString.find("cm") == 0:
        kubeArg = "secret"
        if cmdString.find("cm")==0:
            kubeArg = "cm"
        cmdStringList = cmdString.split()
        if len(cmdStringList) == 1:
            cmdString = "ku get %s" % kubeArg
        elif len(cmdStringList) == 2:
            cmdString = "ku get %s %s -o yaml" % (kubeArg, cmdStringList[1])
        elif len(cmdStringList) >=3:
            jsonPath = cmdStringList[2]
            jsonPath = jsonPath.replace(".","\\.")
            cmdString = "ku get %s %s -o jsonpath='{.data.%s}'" % (kubeArg, cmdStringList[1], jsonPath)
            if len(cmdStringList) == 4 and cmdStringList[3] == "--decode":
                doBase64decode=True
            if kubeArg == "secret" and len(cmdStringList) == 4 and cmdStringList[3] == "--cert":
                doBase64decode=True
                isCertificate = True

    cmdString = getShellCmd(namespace, cmdString)

    # if cmdString.find("node") == 0:
    #     selectedNode=applicationState.selected_node
    #     options=cmdString.replace("node","").strip()
    #     text=nodes.describe(options,selectedNode)
    #     if options == "":
    #         options = selectedNode
    #     cmdString = "describe node %s " % options

    if cmdString.find("delete") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            force=False
            if (cmdString.find("--force") > -1):
                force=True
            text=pods.delete(resourceName,namespace,force)
            cmdString = "delete pod %s" % resourceName
            #refreshUIAfterCmd = True
        else:
            text = "ERROR: delete is available only for pods."

    if cmdString.find("shell") == 0:
        shellCmd = cmdString.replace("shell","").strip()
        text=cmd.executeCmd(shellCmd)

    if doBase64decode == True:
        #text is assumed to hold base64 string, from secret or cm command
        text = text.replace("'","")
        text = base64.b64decode(text)
        text = str(text,"utf8")
    
    if isCertificate == True:
        #text is assumed to be certificate and openssl tool is assumed to present
        import subprocess,os
        fName = ".cert.tmp"
        certFile = open(fName,"w")
        certFile.write(text)
        certFile.close()
        text = subprocess.check_output(["openssl", "x509", "-text", "-noout", 
                                "-in", fName],stderr=subprocess.STDOUT,timeout=30)
        text = str(text,'utf-8')
        if os.path.exists(fName):
            os.remove(fName)

    if cmdString.find("exec") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            command = cmdString.replace("exec","").strip()
            cmdString = "exec %s %s" % (resourceName,command)
            text=pods.exec(resourceName,namespace,command)
        else:
            text = "ERROR: exec is available only for pods."


    if cmdString.find("top") == 0:
        topCmd=cmdString
        if cmdString.find("-l") > -1:
            cmdString = cmdString.replace("-l","label")
        if cmdString.find("-c") > -1:
            cmdString = "top pod %s" % (resourceName)
        if cmdString.find("-n") > -1:
            cmdString = "top nodes"
        
        doAsciiGraph=False
        if topCmd.find("-g") > -1:
            doAsciiGraph = True
            topCmd = topCmd.replace("-g","")

        
        text=pods.top(resourceName,namespace,topCmd,isAllNamespaces(),doAsciiGraph)

    if cmdString.find("cls") == 0:
        clearOutputWindow()

    if cmdString.find("wrap") == 0:
        toggleWrap()

    if cmdString.find("/") == 0:
        #searching
        applicationState.searchString=cmdString[1:]
        #appendToOutput("TODO: search: %s" % applicationState.searchString, cmdString=cmdString)

    if cmdString.find("save") == 0:
        #save Output-window to a file
        cmdArgs = cmdString.split()
        if len(cmdArgs) > 1:
            #filename is the second argument
            filename = cmdArgs[1]
        else:
            filename = "kubeterminal_output_%s.txt" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(filename, "w") as outputFile:
            outputFile.write(outputArea.text)
        text="Output saved to file '%s'." % filename


    if cmdString.find("work") == 0:
        #worker node statistics

        params=[]
        if cmdString.find("-d") > -1:
           params.append("describe")
 
        nodeStats = nodes.describeNodes("worker",params)
        
        text=nodeStats

    if cmdString.find("clip") == 0:
        #copy output window contents to clipboard
        import pyperclip
        pyperclip.copy(outputArea.text)
        text="Output window contents copied to clipboard."

    if cmdString.find("use-context") == 0:
        if applicationState.content_mode == globals.WINDOW_CONTEXT:
            selectedContext = applicationState.selected_pod
            cmdString = "use-context %s" % (selectedContext)
            text="TODO: change context to %s" % (selectedContext)
            #text = "\n".join(namespaceWindow.values)
            #change values like this
            #namespaceWindow.values = [("jee","jee")]
            #update namespaces and nodes
            pass
        else:
            text = "ERROR: use-context is only available for contexts."

    if cmdString.find("win") == 0:
        #window command to select content for "pod"-window
        cmdArgs = cmdString.split()
        showAvailableWindowsHelpText = False
        if len(cmdArgs) > 1:
            windowName = "WINDOW_%s" % (cmdArgs[1].upper())
            if windowCmd.windowExists(windowName) == True:
                applicationState.content_mode = windowName#"WINDOW_%s" % (windowName)
                #if window is context then update current context variable
                if applicationState.content_mode == globals.WINDOW_CONTEXT:
                    applicationState.current_context = cmd.getCurrentContext()
                    #store namespace and resource name that are selected before moving to non resource window like context
                    (applicationState.resource_namespace,applicationState.resource_resourceName)=getResourceNameAndNamespaceName()
                    text = "Current context:\n" + applicationState.current_context
                    text = text+ "\n\nSelect context and enter command 'use-context' or use ctrl-u to change context."
                updateUI("namespacepods")
            else:
                windowArg = cmdArgs[1]
                if windowArg != "list":
                  text = "Window '%s' does not exist.\n\n" % cmdArgs[1]
                showAvailableWindowsHelpText = True
        else:
            showAvailableWindowsHelpText = True
            text = ""
        if showAvailableWindowsHelpText == True:
            text = "%sAvailable windows:\n" % text
            for idx, resourceType in enumerate(globals.WINDOW_LIST):
                text="%swindow %s (Alt-%d)\n" % (text,resourceType.lower().replace("window_",""),idx+1)

    if cmdString.find("context") == 0:
      #context command to show contexts
      #cmdArgs = cmdString.split()
      (text,title) = windowCmd.getContextList()
      text = "Available contexts:\n%s" % text
      currentContext = cmd.getCurrentContext()
      text = "Current context:\n%s\n\n%s" % (currentContext, text)

    if text != "":
        appendToOutput(text,cmdString=cmdString)
        #appendToOutput("\n".join([outputArea.text,text]),cmd=cmd)
        #outputArea.text="\n".join([outputArea.text,text])
    
    if refreshUIAfterCmd == True:
        updateUI("namespacepods")
        
def commandPrompt(line_number, wrap_count):
    return "command>"

def clearOutputWindow():
    outputArea.text = ""

def toggleWrap():
    outputArea.wrap_lines = not outputArea.wrap_lines

command_container = TextArea(text="", multiline=False,accept_handler=commandHander,get_line_prefix=commandPrompt)
commandWindowFrame= Frame(command_container,title="KubeTerminal (Ctrl-d to describe pod, Ctrl-l to show logs, Esc to exit, Tab to switch focus and refresh UI, 'help' for help)",height=4)


root_container = HSplit([content_container, 
     #           HorizontalLine(),
                #Window(height=1, char='-'),
                commandWindowFrame])

layout = Layout(root_container)

#call before render only when app is started the first time
#=> sets content to pod window
started=False
def before_render(application):
    global started
    if started == False:
        updateState()
        started = True
        if args.no_help == False:
          executeCommand("help")

app = Application(layout=layout,
                key_bindings=kb,
                full_screen=True,             
                mouse_support=enableMouseSupport,
                before_render=before_render
                )
app.run()