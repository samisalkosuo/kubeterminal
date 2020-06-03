from .cmd import executeCmd
import os

def isForbiddenAllNamespace():
    output = executeCmd("%s get namespaces" % os.environ["KUBETERMINAL_CMD"])
    return output.find("Forbidden") > -1

def isForbiddenNodes():
    output = executeCmd("%s get nodes" % os.environ["KUBETERMINAL_CMD"])
    return output.find("Forbidden") > -1


