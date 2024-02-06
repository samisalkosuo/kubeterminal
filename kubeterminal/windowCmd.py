#from application import globals
import kubeterminal.globals as globals
from .pods import list as podList
from .cmd import getResources, getContexts

def windowExists(windowName):
    return windowName in globals.WINDOW_LIST

#returns true if window mode resource is global, like storageclass
def isGlobalResource(content_mode):

    isGlobal = False
    if content_mode == globals.WINDOW_SC or \
       content_mode == globals.WINDOW_PV or \
       content_mode == globals.WINDOW_NODE or \
       content_mode == globals.WINDOW_CRD or \
       content_mode == globals.WINDOW_NAMESPACE \
        :
        isGlobal = True

    return isGlobal

def getCommandWindowTitle(content_mode, namespace, selected_node, selected_resource):
    title = ""
    if content_mode == globals.WINDOW_POD:
        title = "NS: %s, NODE: %s, POD: %s" % (namespace,selected_node,selected_resource)
    else:
        resourceType = globals.WINDOW_COMMAND_WINDOW_TITLE[content_mode]        
        title = "NS: %s, %s: %s" % (namespace,resourceType, selected_resource)
    
    return title

def getResourceType(content_mode):
    resourceType = globals.WINDOW_RESOURCE_TYPE[content_mode]    
    return resourceType

def getWindowContentAndTitle(content_mode, namespace, selected_node):

    contentList = ""
    title = ""
    resourceType = None
    if content_mode == globals.WINDOW_POD:
        resourceType = globals.WINDOW_POD
        (contentList,title) = getPods(namespace,selected_node)
        
    if content_mode == globals.WINDOW_CONTEXT:
        resourceType = globals.WINDOW_CONTEXT
        (contentList,title) = getContextList()

    if resourceType == None:
        resourceType = globals.WINDOW_RESOURCES_WINDOW_TITLE[content_mode]
        (contentList,title) = getListAndTitle(resourceType, namespace)

    return (contentList, title)

def getPods(namespace, nodes):
    contentList=podList(namespace,nodes)
    podCount = len(contentList.split("\n"))
    title="%d Pods (ns: %s, nodes: %s)" % (podCount, namespace, nodes)
    return (contentList, title)

def getContextsList():
    contentList=getContexts()
    return contentList

def getContextList():
    contentList=getContexts()
    podCount = len(contentList)
    title="%d Contexts" % (podCount)
    return ("\n".join(contentList), title)

def getListAndTitle(resourceType, namespace):
    contentList=getResources(resourceType, namespace)
    podCount = len(contentList)
    title="%d %s (ns: %s)" % (podCount, resourceType, namespace)
    return ("\n".join(contentList), title)


