
from .cmd import getNamespaces

def list():
    '''Return list of tuples of namespaces: [(value,label),(value,label),...]'''
    namespaces = [("all-namespaces","All namespaces")]
    allNamespaces =  getNamespaces()
    
    for ns in allNamespaces:
        namespaces.append((ns,ns))

    return namespaces