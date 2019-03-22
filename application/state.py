

#Application state on module

current_namespace=""
selected_pod=""
selected_node="all"
searchString=""


class State(object):

    def __init__(self):
        self.current_namespace=""
        self.selected_pod=""
        self.selected_node="all"