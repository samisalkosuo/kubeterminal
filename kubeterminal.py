import datetime
import base64
import re
import argparse 
import os, sys
import pathlib
import csv

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
#pubsub
from pubsub import pub

#set command before importing 
os.environ["KUBETERMINAL_CMD"] = "kubectl"

from kubeterminal import pods,nodes,windowCmd
from kubeterminal import state,lexer
from kubeterminal import cmd 
from kubeterminal import globals
from kubeterminal import permissions


def fileExistsType(filePath):
    path = pathlib.Path(filePath)
    if path.is_file() == False:
        raise argparse.ArgumentTypeError('KUBECONFIG file %s does not exist.' % filePath)
    else:
        return filePath

#CLI args
parser = argparse.ArgumentParser()
parser.add_argument('--no-dynamic-title', action="store_true", help='Do not set command window title to show NS, node and pod.')
parser.add_argument('--compact-windows', action="store_true", help='Set namespace, node and pod windows to more compact size.')
parser.add_argument('--even-more-compact-windows', action="store_true", help='Set namespace, node and pod windows to even more compact size.')
parser.add_argument('--ns-window-size', type=int, default=53, help='Namespace window size. Default is 53 or less.')
parser.add_argument('--kubeconfig', action='append', nargs='+', type=fileExistsType, metavar='KUBECONFIGPATH', help='Set path(s) to kubeconfig auth file(s).')
parser.add_argument('--current-kubeconfig', type=fileExistsType, help='Set path to current/active kubeconfig auth file.')
parser.add_argument('--oc', action="store_true", help='Use oc-command instead of kubectl.')
parser.add_argument('--no-help', action="store_true", help='Do not show help when starting KubeTerminal.')
parser.add_argument('--print-help', action="store_true", help='Print KubeTerminal help and exit.')
args = parser.parse_args()

if args.oc == True:
    os.environ["KUBETERMINAL_CMD"] = "oc"

kubeconfigFiles = []
#find all kubeconfig-files
#assume all are named kubeconfig
path = "/"
for root,d_names,f_names in os.walk(path):
    for f in f_names:
        if f == "kubeconfig":
            kubeconfigFiles.append(os.path.join(root, f))

if args.kubeconfig:
    for kubeconfigArgs in args.kubeconfig:
        for kubeconfigFile in kubeconfigArgs:
            if not kubeconfigFile in kubeconfigFiles:
                kubeconfigFiles.append(kubeconfigFile)
os.environ["KUBECONFIG_FILES"] = " ".join(kubeconfigFiles)

try:
    if args.current_kubeconfig:
        os.environ["CURRENT_KUBECONFIG_FILE"] = "%s" % args.current_kubeconfig
except:
    pass

helpText = """KubeTerminal

Helper tool for Kubernetes and OpenShift.

Output window shows output of commands.
"Selected pod/resource" is the resource where cursor is in the Resources window.

Key bindings:

ESC           - exit program.
TAB           - change focus to another window.
<alt-u>       - resource window up one line.
<alt-j>       - resource window down one line.
<alt-i>       - resource window page up.
<alt-k>       - resource window page down.
<alt-o>       - output window page up.
<alt-l>       - output window page down.
<alt-0>       - list available windows.
<alt-1>       - show pods.
<alt-2>       - show configmaps.
<alt-3>       - show services.
<alt-4>       - show secrets.
<alt-5>       - show statefulsets.
<alt-6>       - show replicasets.
<alt-7>       - show daemonsets.
<alt-8>       - show persistentvolumeclaims.
<alt-9>       - show persistentvolumes.
<alt-10>      - show deployments.
<alt-11>      - show storageclasses.
<alt-12>      - show jobs.
<alt-13>      - show cronjobs.
<alt-14>      - show roles.
<alt-15>      - show rolebindings.
<alt-16>      - show serviceaccounts.
<alt-17>      - show poddisruptionbudgets.
<alt-18>      - show routes.
<alt-19>      - show ingresses.
<alt-20>      - show nodes.
<alt-21>      - show customresourcedefinitions.
<alt-22>      - show namespaces.
<alt-c>       - show kubeconfig and context.
<alt-shift-l> - show logs of currently selected pod.
<alt-shift-r> - refresh namespace and node windows.
<alt-d>       - show description of currently selected resource.
<alt-y>       - show YAML of currently selected resource.
<alt-r>       - refresh resource (pod etc.) list.
<alt-g>       - to the end of Output-window buffer.
<alt-w>       - toggle wrapping in Output-window.
/             - search string in Output-window.

Commands:

help                                  - this help.
all                                   - show all resources in namespaces.
clip                                  - copy Output-window contents to clipboard.
cls                                   - clear Output-window.
context [<cxt_index>]                  - show current and available contexts or set current context.
decode <data key> [cert}              - decode base64 encoded secret or configmap value, optionally decode certificate.
delete [--force]                      - delete currently selected pod, optionally force delete.
describe                              - describe currently selected resource.
exec [-c <container_name>] <command>  - exec command in currently selected pod.
json                                  - get JSON of currently selected resource.
ku <cmds/opts/args>                   - execute kubectl in currently selected namespace.
kubeconfig [<config_index>]           - list kubeconfigs or set current config.
labels                                - show labels of currently selected pod.
logs [-c <container_name>]            - show logs of currently selected pod.
oc <cmds/opts/args>                   - execute oc in currently selected namespace.
save [<filename>]                     - save Output-window contents to a file.
shell <any shell command>             - executes any shell command.
top [-c | -l <label=value> | -n | -g] - show top of pods/containers/labels/nodes. Use -g to show graphics.
version                               - Show 'kubectl' and 'oc' version information.
window [<window name> | list]         - Set resource type for window. 'window list' lists available windows.
workers [-d]                          - get worker node resource allocation. Use -d to describe all worker nodes.
wrap                                  - toggle wrapping in Output-window.
yaml                                  - get YAML of currently selected resource.

"""

if args.print_help == True:
    print(helpText)
    exit(0)

from enum import Enum
class WindowName(Enum):
    resource = "ResourceWindow"
    output = "OutputWindow"
    command = "CommandWindow"

class Direction(Enum):
    up = "up"
    down = "down"


applicationState = state#state.State()

applicationState.content_mode=globals.WINDOW_POD

#get max node length in window
nodesList = nodes.list()

longestNodeLine=0
for node in nodesList:
    L = len(node[1])
    if L > longestNodeLine:
        longestNodeLine = L
#+8 added to inclucde radiolist checkboxes and window borders and space at the end of line
longestNodeLine = longestNodeLine + 8
if longestNodeLine > args.ns_window_size:
  longestNodeLine = args.ns_window_size

namespaceWindowSize=27
nodeWindowSize = longestNodeLine
podListWindowSize = namespaceWindowSize + longestNodeLine #pod list window size max 80
isCompactWindows=False
if args.compact_windows == True:
    namespaceWindowSize=20
    nodeWindowSize=30
    podListWindowSize=50
    isCompactWindows=True
if args.even_more_compact_windows == True:
    namespaceWindowSize=20
    nodeWindowSize=10
    podListWindowSize=30
    isCompactWindows=True
if permissions.isForbiddenNodes() == True and isCompactWindows==False:
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
        
        #TODO truncate long namespaces only in podlistarea, show full namespace in title window
        # if isAllNamespaces() == True:
        #     rows = contentList.split("\n")
        #     newContentList = []
        #     for row in rows:
        #         columns = row.split()
        #         namespace = columns[0]
        #         namespace = (namespace[:25] + '..') if len(namespace) > 27 else namespace
        #         namespace = namespace.ljust(27)

        #         columns[0] = namespace
        #         row = "   ".join(columns)
        #         newContentList.append(row)
            
                
        #     contentList = "\n".join(newContentList)

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

@kb.add('escape','d')
def describepod_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("describe")

@kb.add('escape','y')
def yamlResource_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("yaml")

@kb.add('escape','L')
def logspod_(event):
    applicationState.selected_pod=str(podListArea.buffer.document.current_line).strip()
    executeCommand("logs")

@kb.add('escape','r')
def refreshpods_(event):
    #refresh pod window
    refreshWindows(refreshPodWindowOnly = True)

@kb.add('escape','R')
def refreshnsnodes_(event):
    #refresh namespace/node windows
    refreshWindows()

@kb.add('escape','g')
def toendofoutputbuffer_(event):    
    outputArea.buffer.cursor_down(outputArea.document.line_count)

@kb.add('escape','w')
def togglewrap_(event):    
    toggleWrap()

#window scroll keybindings use alt modified and letters uiojkl
#because various terminals have their own keybindings that interfere
#for example, powershell has ctrl-j and putty/screen did not accept ctrl - cursor keys
@kb.add('escape','j')
def _(event):
    windowScroll(WindowName.resource, Direction.down)

@kb.add('escape','k')
def _(event):
    windowScroll(WindowName.resource, Direction.down, page = True)

@kb.add('escape','u')
def _(event):
    windowScroll(WindowName.resource, Direction.up)

@kb.add('escape','i')
def _(event):
    windowScroll(WindowName.resource, Direction.up, page = True)

@kb.add('escape','l')
def _(event):
    windowScroll(WindowName.output, Direction.down, page = True)

@kb.add('escape','o')
def _(event):
    windowScroll(WindowName.output, Direction.up, page = True)


def changeWindow(windowName):
    updateState()
    executeCommand("window %s" % windowName)

@kb.add('escape','c')
def _(event):
    executeCommand("kubeconfig")
    executeCommand("context")

@kb.add('escape','0')
def _(event):
    executeCommand("windows")
#key shortcuts to all windows alt-1 - alt-xx
for index, windowName in enumerate(globals.WINDOW_LIST, start=1):

    if index < 10:
      #Alt-1 - 9
      @kb.add('escape',str(index))
      def _(event):
        keySequence = event.key_sequence
        if len(keySequence) == 2:
            windowIndex = int(keySequence[1].key) - 1 
            wn = globals.WINDOW_LIST[windowIndex]
            changeWindow(globals.WINDOW_RESOURCE_TYPE[wn])

    else:
      #Alt-10 - 99
      numbers = str(index)
      @kb.add('escape',numbers[0],'escape',numbers[1])
      def _(event):
        keySequence = event.key_sequence
        if len(keySequence) == 4:
            ki1 = int(keySequence[1].key) 
            ki2 = int(keySequence[3].key) 
            windowIndex = int("%d%d" % (ki1, ki2)) - 1
            wn = globals.WINDOW_LIST[windowIndex]
            changeWindow(globals.WINDOW_RESOURCE_TYPE[wn])


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

def isAllNamespaces():
    return applicationState.current_namespace == "all-namespaces"

#scroll/move cursor in resource or output window
def windowScroll(bufferName, direction, page = False):

    for w in layout.get_visible_focusable_windows():
        try:
            buffer = w.content.buffer
            linesToScroll = 1
            if page == True:
                #if page is true then scroll page up or down
                renderInfo = w.render_info
                #window height is number of lines in the window
                windowHeight = renderInfo.window_height
                if direction == Direction.down:
                    if buffer.document.cursor_position_row < windowHeight:
                      linesToScroll = 2 * windowHeight - 2
                    else: 
                      linesToScroll = windowHeight - 1
                if direction == Direction.up:
                    linesToScroll = windowHeight - 1
                    if buffer.document.cursor_position_row > buffer.document.line_count - windowHeight:
                      linesToScroll = 2 * windowHeight - 2

            if (bufferName == WindowName.resource or bufferName == WindowName.output) and buffer.name == bufferName:
                if direction == Direction.down:
                    buffer.cursor_down(linesToScroll)
                if direction == Direction.up:
                    buffer.cursor_up(linesToScroll)

        except:
            #ignore errors, such as buffer not found in window
            pass


def appendToOutput(text, cmdString = "", overwrite = False):

    if text is None or "No resources found" in text:    
        return
    
    #TODO: option to set UTC or local
    #now = datetime.datetime.utcnow().isoformat()
    now = datetime.datetime.now().isoformat()
    if cmdString == "" or cmdString == None:
        header = "=== %s ===" % now
    else:
        header = "=== %s %s ===" % (now,cmdString)
    
    if outputArea.text == "":        
        outputArea.text="\n".join([header,text,""])
    else:
        outputArea.text="\n".join([outputArea.text,header,text,""])
    
#    outputArea.buffer.cursor_position=len(outputArea.text)
    outputIndex=outputArea.text.find(header)
    outputArea.buffer.cursor_position=outputIndex#len(outputArea.text)
    outputArea.buffer.cursor_down(30)

#TODO: combine this function, getKubectlCommand-function in cmd.py and also code in executeCommand-function.
def getShellCmd(current_namespace, namespace, cmdString):
    
    if cmdString.find("ku ") == 0 or cmdString.find("oc ") == 0:
        cmdName = "kubectl"
        if cmdString.find("oc ") == 0:
            cmdName = "oc"
        #add kubeconfig
        cmdName = "%s %s" % (cmdName, cmd.getKubeConfigFile())

        #command arguments af "oc" or "ku"
        cmdArgs = cmdString[2:].strip()
        #namespace argument added if not global resource like storageclass
        namespaceArg = ""        
        if windowCmd.isGlobalResource(applicationState.content_mode) == False:
            # if current_namespace == "all-namespaces":
            #     cmdArgs = "%s --all-namespaces" % cmdArgs
            # else:
            namespaceArg = "-n %s" % namespace
            
        cmdString  = "shell %s %s %s" % (cmdName, namespaceArg, cmdArgs)
    
    return cmdString

#command handler for shell
def commandHander(buffer):
    #check incoming command
    cmdString = buffer.text
    executeCommand(cmdString)

def refreshWindows(refreshPodWindowOnly = False):
    if refreshPodWindowOnly == False:
        cliApplication.refreshNamespaceAndNodeWindows()
    updateState()
    updateUI("namespacepods")


#actual command handler, can be called from other sources as well
def executeCommand(cmdString):
    import os#os imported also here because import at the beginning is not in this scope...
    refreshUIAfterCmd = False
    text=""
    cmdcmdString = cmdString.strip()
    originalCmdString = cmdcmdString
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
                cmd.getLogs(resourceName,namespace,options)                
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

    doBase64decode = False
    decodeCert = False
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
                #cmdString = "%s %s %s --decode " % (cmdString,resourceName, key)
                cmdString = "%s %s %s " % (cmdString,resourceName, key)
                doBase64decode = True
                if cmdArgs[-1] == "cert":
                    #decode command includes 'cert' => use openssl to show cert
                    decodeCert = True
            else:
                text = "ERROR: No key name given."
        else:
            text = "ERROR: Decode available only for secrets and configmaps."

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

    cmdString = getShellCmd(applicationState.current_namespace, namespace, cmdString)

    #if directly using oc or ku command do not add namespace
    #but add kubeconfig
    if originalCmdString.find("ku ") == 0:
        #kubectl        
        cmdString = originalCmdString.replace("ku ","shell kubectl ")
        cmdString = "%s %s " % (cmdString, cmd.getKubeConfigFile())

    if originalCmdString.find("oc ") == 0:
        #oc
        cmdString = originalCmdString.replace("oc ","shell oc ")
        cmdString = "%s %s " % (cmdString, cmd.getKubeConfigFile())

    if cmdString.find("all") == 0:
        ns = "-n %s" % namespace
        if isAllNamespaces() == True:
            ns = "-A"
        cmdString = "shell oc %s get all %s" % (cmd.getKubeConfigFile(), ns)

    if cmdString.find("delete") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            force=False
            if (cmdString.find("--force") > -1):
                force=True
            text=cmd.deletePod(resourceName,namespace,force)
            cmdString = "delete pod %s" % resourceName
            #refreshUIAfterCmd = True
        else:
            text = "ERROR: delete is available only for pods."

    if cmdString.find("shell") == 0:
        shellCmd = cmdString.replace("shell","").strip()
        #text=cmd.executeCmd(shellCmd)
        cmd.ExecuteCommandBackground(shellCmd, publishOutput = True,decodeBase64 = doBase64decode, decodeCert = decodeCert)

    if cmdString.find("version") == 0:
        text1=cmd.executeCmd("kubectl version")
        text2=cmd.executeCmd("oc version")
        text = "Kubernetes:\n%s\nOpenShift:\n%s" % (text1, text2)

    if cmdString.find("exec") == 0:
        if applicationState.content_mode == globals.WINDOW_POD:
            command = cmdString.replace("exec","").strip()
            cmdString = "exec %s %s" % (resourceName,command)
            text=cmd.execCmd(resourceName,namespace,command)
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
        cmdArgs = cmdString.split()
        if len(cmdArgs) == 1:
            #context command to show contexts
            contextList = windowCmd.getContextsList()
            (text,title) = windowCmd.getContextList()
            text = "Available contexts:\n%s" % text
            currentContext = cmd.getCurrentContext()
            text = "Current context:\n%s\n\nAvailable contexts:\n" % (currentContext)
            i = 0
            for context in contextList:
                text = "%s%d: %s\n" % (text,i,context)
                i = i + 1
            text = "%s\n\nUse 'context <NR>' command to change context." % (text)
        else:
            selectedContext=int(cmdString.split()[1]) 
            contextList = windowCmd.getContextsList()
            selectedContext = contextList[selectedContext] 
            cmdString = "kubectl config use-context %s" % (selectedContext)
            #cmd.ExecuteCommandBackground(cmdString, publishOutput = True,decodeBase64 = doBase64decode, decodeCert = decodeCert)
            cmd.executeCmd(cmdString)
            refreshWindows()
            
    if cmdString.find("kubeconfig") == 0:
        cmdArgs = cmdString.split()
        if len(cmdArgs) > 1:
            if "KUBECONFIG_FILES" in os.environ:
                #kubeconfig index given
                index = int(cmdArgs[1])
                if index == 0:
                    #clear kubeconfig
                    if "CURRENT_KUBECONFIG_FILE" in os.environ:
                        del os.environ["CURRENT_KUBECONFIG_FILE"]                        
                else:
                    os.environ["CURRENT_KUBECONFIG_FILE"] = os.environ["KUBECONFIG_FILES"].split()[index-1]
                refreshWindows()
            else:
                text = "%sNo kubeconfigs available." % (text)
        else:
            #list given kubeconfigs
            currentContext = cmd.getCurrentContext()
            text = "Current context:\n%s\n\n" % (currentContext)
            text = "%sCurrent kubeconfig:\n" % (text)
            if "CURRENT_KUBECONFIG_FILE" in os.environ and os.environ["CURRENT_KUBECONFIG_FILE"] != None:
                text = "%s%s\n" % (text,os.environ["CURRENT_KUBECONFIG_FILE"])
            else:
                text = "%s<no current kubeconfig>\n" % (text)
            text = "%s\nKubeconfigs:\n" % (text)
            text = "%s0: <clear kubeconfig file>\n" % (text)
            if "KUBECONFIG_FILES" in os.environ:
                index = 1
                for cfg in os.environ["KUBECONFIG_FILES"].split():
                    text = "%s%d: %s\n" % (text, index, cfg)
                    index = index + 1
            else:
                text = "%sNo kubeconfigs available." % (text)
            text = "%s\n\nUse 'kubeconfig <NR>' command to change kubeconfig." % (text)

    if cmdString.find("login") == 0:
        text = "TODO: login command"

    #generic test commande
    if cmdString.find("testcmd") == 0:
        #text = cliApplication.refreshWindows()
        text="test command used during development"
        pub.sendMessage('working',arg="started")

    #refresh windows
    if cmdString.find("refresh") == 0:
        refreshWindows()

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

#pubsub listeners and subscriptions
def listener_print_logs(arg,arg2 = None):
    index = arg.find("choose one of: [")
    if index > -1:
        text1 = arg[0:index]
        text2 = arg[index:]
        text2 = text2.replace("choose one of: [","choose one of:\n[")
        text = "%s\n%s" % (text1, text2)
    else:
        text = arg
    appendToOutput(text, cmdString = arg2)
pub.subscribe(listener_print_logs, 'print_logs')

def listener_print_output(arg,arg2 = None):
    appendToOutput(arg, cmdString = arg2)
pub.subscribe(listener_print_output, 'print_output')

backgroundProcessesInProgress = 0
def listener_background_processing_start(arg):
    global backgroundProcessesInProgress
    backgroundProcessesInProgress = backgroundProcessesInProgress + 1
    if (backgroundProcessesInProgress == 1):
        outputAreaFrame.title = "Output (Background process in progress)"#: %s)" % (outputAreaFrame.title, arg)
    if (backgroundProcessesInProgress > 1):
        outputAreaFrame.title = "Output (%d background processes in progress)" % backgroundProcessesInProgress#: %s)" % (outputAreaFrame.title, arg)

def listener_background_processing_stop(arg=None):
    global backgroundProcessesInProgress
    backgroundProcessesInProgress = backgroundProcessesInProgress - 1
    if (backgroundProcessesInProgress == 0):
        outputAreaFrame.title = "Output"
    if (backgroundProcessesInProgress == 1):
        outputAreaFrame.title = "Output (Background process in progress)"#: %s)" % (outputAreaFrame.title, arg)
    if (backgroundProcessesInProgress > 1):
        outputAreaFrame.title = "Output (%d background processes in progress)" % backgroundProcessesInProgress#: %s)" % (outputAreaFrame.title, arg)

pub.subscribe(listener_background_processing_start, 'background_processing_start')
pub.subscribe(listener_background_processing_stop, 'background_processing_stop')


#TODO: clarify UI creation

def setNamespaceAndNodeWindowContents():
    global namespaceList, nodesList, namespaceWindow, windowHeight, namespaceWindowFrame
    global nodeListArea, nodeWindowFrame, upper_left_container
    namespaceList = cmd.listNamespaces()
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

#initialize namespace and node windows
setNamespaceAndNodeWindowContents()

#pods window
podListArea = TextArea(text="", 
                multiline=True,
                wrap_lines=False,
                scrollbar=enableScrollbar,
                lexer=lexer.ResourceWindowLexer(),
                read_only=True
                )

#add listener to cursor position changed
podListArea.buffer.on_cursor_position_changed=Event(podListArea.buffer,podListCursorChanged)
podListArea.buffer.name = WindowName.resource
podListArea.window.cursorline = to_filter(True)
podListAreaFrame = Frame(podListArea,title="Pods",width=podListWindowSize)

#output area to output debug etc stuff
outputArea = TextArea(text="", 
                    multiline=True,
                    wrap_lines=False,
                    lexer=lexer.OutputWindowLexer(),
                    scrollbar=enableScrollbar,
                    read_only=True)
outputArea.buffer.name = WindowName.output
outputAreaFrame= Frame(outputArea,title="Output")

#command area
command_container = TextArea(text="", multiline=False,accept_handler=commandHander,get_line_prefix=commandPrompt)
command_container.buffer.name = WindowName.command
commandWindowFrame= Frame(command_container,title="KubeTerminal (Ctrl-d to describe pod, Ctrl-l to show logs, Esc to exit, Tab to switch focus and refresh UI, 'help' for help)",height=4)


def setLayoutContainers():
    global left_container, content_container
    global root_container, layout
    
    left_container = HSplit([upper_left_container, 
                    #HorizontalLine(),
                    #Window(height=1, char='-'),
                    podListAreaFrame])

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

    root_container = HSplit([content_container, 
        #           HorizontalLine(),
                    #Window(height=1, char='-'),
                    commandWindowFrame])

    layout = Layout(root_container)

#from
#https://stackoverflow.com/questions/47517328/prompt-toolkit-dynamically-add-and-remove-buffers-to-vsplit-or-hsplit
class MyApplication(Application):

    def __init__(self, layout, key_bindings, full_screen,mouse_support,before_render):
        #Initialise with the first layout
        super(MyApplication, self).__init__(
            layout=layout,
            key_bindings=key_bindings,
            full_screen=full_screen,
            mouse_support=mouse_support,
            before_render=before_render
        )

    def refreshNamespaceAndNodeWindows(self):
        setNamespaceAndNodeWindowContents()
        setLayoutContainers()
        # Update to use a new layout
        self.layout = layout

#set window containers
setLayoutContainers()

#call 'before render'-function only when app is started the first time
#=> sets content to pod window
started=False
def before_render(application):
    global started
    if started == False:
        updateState()
        started = True
        if args.no_help == False:
          executeCommand("help")
        #set started to env to be used in cmd.py
        os.environ["KUBETERMINAL_IS_STARTED"] = "yes"

cliApplication = MyApplication(layout=layout,
                key_bindings=kb,
                full_screen=True,             
                mouse_support=enableMouseSupport,
                before_render=before_render
                )

cliApplication.run()