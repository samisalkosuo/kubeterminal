

#Application state on module

current_namespace = ""
selected_pod = ""
selected_node = "all"
searchString = ""
cursor_line = 0
content_mode = ""
current_context = ""

#variables that hold namespace and resource name that were selected before switching
#to non-resource window like context
resource_namespace = ""
resource_resourceName = ""

class State(object):

    def __init__(self):
        self.current_namespace = ""
        self.selected_pod = ""
        self.selected_node = "all"
        self.cursor_line = 0
        self.current_context = ""
        self.resource_namespace = ""
        self.resource_resourceName = ""
