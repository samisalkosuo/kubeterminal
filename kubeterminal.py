import datetime

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

from kubectl import namespaces,pods,nodes
from application import state,lexer
from kubectl import cmd 

applicationState = state#state.State()

enableMouseSupport = False
enableScrollbar = False


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
        updateUI("namespacepods")

    if applicationState.selected_node != selected_node:
        applicationState.selected_node = selected_node
        updateUI("nodepods")

def updateUI(updateArea):
    
    if updateArea == "selectedpod":
        appendToOutput(applicationState.selected_pod)

    if updateArea == "nodepods" or updateArea == "namespacepods":
        ns = applicationState.current_namespace
        podsList=pods.list(ns,applicationState.selected_node)
        podCount = len(podsList.split("\n"))
        title="%d Pods (ns: %s, nodes: %s)" % (podCount,ns, applicationState.selected_node)
        podListArea.text=podsList
        podListAreaFrame.title=title


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
namespaceWindow = RadioList(namespaces.list())
namespaceWindowFrame= Frame(namespaceWindow,title="Namespaces",height=8,width=27)

nodeListArea = RadioList(nodes.list())

nodeWindowFrame= Frame(nodeListArea,title="Nodes",height=8,width=53)

upper_left_container = VSplit([namespaceWindowFrame, 
                #HorizontalLine(),
                #Window(height=1, char='-'),
                nodeWindowFrame])

#listens cursos changes in pods list
def podListCursorChanged(buffer):
    pass
    #appendToOutput(buffer.document.current_line)
    #from prompt_toolkit.application import get_app
    #get_app().invalidate()
    #updateUI("nodepods")
    #print("jee: ",buffer.document.current_line)


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
podListAreaFrame = Frame(podListArea,title="Pods",width=80)

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


#command handler for shell
def commandHander(buffer):
    #check incoming command
    cmdString = buffer.text
    executeCommand(cmdString)

#actual command handler, can be called from other sources as well
def executeCommand(cmdString):
    refreshUIAfterCmd = False
    text=""
    if cmdString == "":
        return

    if cmdString == "help":
        text="""KubeTerminal

Helper tool for Kubernetes.

This output window shows output of commands.
"Selected pod" is the pod where cursor is in the Pods window.

Key bindings

- ESC - exit program.
- <ctrl-l>, show logs of currently selected pod (without any options).
- <ctrl-d>, show description of currently selected pod (without any options).
- <ctrl-r>, refresh pod list.
- <shift-g>, to the end of Output-window buffer.
- / -  search string in Output-window.

Commands:

- help - this help.
- cls - clear Output-window.
- delete [--force] - delete currently selected pod, optionally force delete.
- describe <describe options> - show description of currently selected pod.
- exec [-c <container_name>] <command> - exec command in currently selected pod.
- json - get JSON of currently selected pod.
- logs <options> - show logs of currently selected pod.
- node <node name> - show description of given node, or currently selected node.
- save [<filename>] - save Output-window contents to a file.
- shell <any shell command> - executes any shell command.
- yaml - get YAML of currently selected pod.

"""
    def getPodNameAndNamespaceName():
        podLine = applicationState.selected_pod
        namespace=""
        podName=""
        if podLine != "":
            fields=podLine.split()
            if applicationState.current_namespace == "all-namespaces":
                podName=fields[1]
                namespace=fields[0]
            else:
                podName=fields[0]
                namespace=applicationState.current_namespace
        return (namespace,podName)

    if cmdString.find("logs") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        if namespace!="" and podName != "":
            options=cmdString.replace("logs","")
            cmdString = "logs " + podName
            text=pods.logs(podName,namespace,options)

    if cmdString.find("describe") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        if namespace!="" and podName != "":
            options=cmdString.replace("describe","")
            cmdString = "describe " + podName
            text=pods.describe(podName,namespace,options) 

    if cmdString.find("yaml") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        if namespace!="" and podName != "":
            text=pods.yaml(podName,namespace) 
            cmdString = "yaml " + podName

    if cmdString.find("json") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        if namespace!="" and podName != "":
            text=pods.json(podName,namespace) 
            cmdString = "json " + podName

    if cmdString.find("node") == 0:
        selectedNode=applicationState.selected_node
        options=cmdString.replace("node","").strip()
        text=nodes.describe(options,selectedNode)
        if options == "":
            options = selectedNode
        cmdString = "describe node %s " % options

    if cmdString.find("delete") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        force=False
        if (cmdString.find("--force") > -1):
            force=True
        text=pods.delete(podName,namespace,force)
        cmdString = "delete pod %s" % podName
        refreshUIAfterCmd = True

    if cmdString.find("shell") == 0:
        shellCmd = cmdString.replace("shell","").strip()
        text=cmd.executeCmd(shellCmd)

    if cmdString.find("exec") == 0:
        (namespace,podName)=getPodNameAndNamespaceName()
        command = cmdString.replace("exec","").strip()
        cmdString = "exec %s %s" % (podName,command)
        text=pods.exec(podName,namespace,command)

    if cmdString.find("cls") == 0:
        clearOutputWindow()

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

command_container = TextArea(text="", multiline=False,accept_handler=commandHander,get_line_prefix=commandPrompt)
commandWindowFrame= Frame(command_container,title="KubeTerminal (Ctrl-d to describe pod, Ctrl-l to show logs, Esc to exit, Tab to switch focus and refresh UI, 'help' for help)",height=4)


root_container = HSplit([content_container, 
     #           HorizontalLine(),
                #Window(height=1, char='-'),
                commandWindowFrame])

layout = Layout(root_container)

app = Application(layout=layout,
                key_bindings=kb,
                full_screen=True,             
                mouse_support=enableMouseSupport
                )
app.run()