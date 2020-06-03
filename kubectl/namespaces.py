
from .cmd import getNamespaces
from .permissions import isForbiddenAllNamespace

def list():
    '''Return list of tuples of namespaces: [(value,label),(value,label),...]'''
    if isForbiddenAllNamespace() == True:
        namespaces = []
    else:
        namespaces = [("all-namespaces","All namespaces")]
    allNamespaces =  getNamespaces()
    
    for ns in allNamespaces:
        namespaces.append((ns,ns))

    return namespaces