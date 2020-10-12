from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
import re
import application.globals as globals

class PodStatusLexer(Lexer):
    
    def allPodsRunning(self, line):
        #return true if all pods are running (line shows 3/3, 1/1, etc.)
        #return false if not all pods are running (line shows 2/3, 0/1, etc.)

        matchObj = re.search( r'([0-9]+)/([0-9]+)', line)

        if matchObj:
            runningNow=int(matchObj.group(1))
            runningTarget=int(matchObj.group(2))
            return runningNow == runningTarget
        else:
           return False

    def podWindowColors(self,line):
        #error, red
        if "CrashLoopBackOff" in line or "Terminating" in line:
            return [(NAMED_COLORS["Red"],line)]

        if "Completed" in line:
            return [(NAMED_COLORS["GreenYellow"],line)]

        #find out running status
        #assume that line includes something like 2/2 or 1/1 or 1/3 
        #to show how many pods are running 
        if self.allPodsRunning(line) == False:
            return [(NAMED_COLORS["Yellow"],line)]

        #All appear to be running, green
        if "Running" in line:
            return [(NAMED_COLORS["Green"],line)]

        #unknown, yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def svcWindowColors(self,line):
        
        if "NodePort" in line:
            return [(NAMED_COLORS["GreenYellow"],line)]

        #default green
        return [(NAMED_COLORS["Green"],line)]


    def cmWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def secretWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def statefulSetWindowColors(self,line):

        #find out running status
        #assume that line includes something like 2/2 or 1/1 or 1/3 
        #to show how many statefulsets are running 
        if self.allPodsRunning(line) == False:
            return [(NAMED_COLORS["Yellow"],line)]

        #default green
        return [(NAMED_COLORS["Green"],line)]

    def replicaSetWindowColors(self,line):

        fields = line.split()
        from .state import current_namespace
        try:
            if current_namespace == "all-namespaces":
                desired = int(fields[2])
                current = int(fields[3])
                ready = int(fields[4])
            else:
                desired = int(fields[1])
                current = int(fields[2])
                ready = int(fields[3])
        except:
            #not a number
            return [(NAMED_COLORS["Yellow"],line)]
        
        #default green
        if desired == current and desired == ready and current == ready:
            return [(NAMED_COLORS["Green"],line)]
        else:
            return [(NAMED_COLORS["Yellow"],line)]

    def daemonSetWindowColors(self,line):

        fields = line.split()
        from .state import current_namespace
        try:
            if current_namespace == "all-namespaces":
                desired = int(fields[2])
                current = int(fields[3])
                ready = int(fields[4])
                uptodate = int(fields[5])
                available = int(fields[6])
            else:
                desired = int(fields[1])
                current = int(fields[2])
                ready = int(fields[3])
                uptodate = int(fields[4])
                available = int(fields[5])
        except:
            #not a number
            return [(NAMED_COLORS["Yellow"],line)]

        #default green
        if desired == current and desired == ready \
            and current == ready and uptodate == current \
            and available == desired and available == uptodate \
            and desired == uptodate and available == desired:
            return [(NAMED_COLORS["Green"],line)]
        else:
            return [(NAMED_COLORS["Yellow"],line)]

    def contextWindowColors(self, line):

        from .state import current_context
        if current_context == line:
            return [(NAMED_COLORS["Green"],line)]
        
        #not current context, yellow
        return [(NAMED_COLORS["Yellow"],line)]
        
    def persistentVolumeClaimsWindowColors(self,line):

        #split line
        fields = line.split()
        #if third field is "Bound" then green
        if fields[2] == "Bound":
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]


    def persistentVolumesWindowColors(self,line):

        #split line
        fields = line.split()
        #if fifth field is "Bound" then green
        if fields[4] == "Bound":
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def deploymentWindowColors(self,line):

        fields = line.split()
        from .state import current_namespace
        ready = "0/1"
        try:
            if current_namespace == "all-namespaces":
                ready = fields[2]
            else:
                ready = fields[1]
        except:
            #not a number
            return [(NAMED_COLORS["Yellow"],line)]

        #ready-field shows 1/1 or similar
        readyFields = ready.split("/")
        current = int(readyFields[0])
        desired = int(readyFields[1])
        if current == desired:
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def storageClassWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def jobWindowColors(self,line):
        fields = line.split()
        from .state import current_namespace
        ready = "0/1"
        try:
            if current_namespace == "all-namespaces":
                ready = fields[2]
            else:
                ready = fields[1]
        except:
            #not a number
            return [(NAMED_COLORS["Yellow"],line)]

        #ready-field shows 1/1 or similar
        readyFields = ready.split("/")
        current = int(readyFields[0])
        desired = int(readyFields[1])
        if current == desired:
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def cronJobWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def roleWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def roleBindingWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def serviceAccountWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def podDisruptionBudgetWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def routeWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def ingressWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def nodeWindowColors(self,line):

        #split line
        fields = line.split()
        #if fifth field is "Bound" then green
        if fields[1] == "Ready":
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def crdWindowColors(self,line):        
        #default green
        return [(NAMED_COLORS["Green"],line)]

    def namespaceWindowColors(self,line):

        #split line
        fields = line.split()
        #if fifth field is "Bound" then green
        if fields[1] == "Active":
            return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]


    def lex_document(self, document):
        #colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))
        def get_line(lineno):
            line = document.lines[lineno]

            #import content mode
            from .state import content_mode
            if content_mode == globals.WINDOW_POD:
                return self.podWindowColors(line)

            if content_mode == globals.WINDOW_SVC:
                return self.svcWindowColors(line)

            if content_mode == globals.WINDOW_CM:
                return self.cmWindowColors(line)

            if content_mode == globals.WINDOW_SECRET:
                return self.secretWindowColors(line)

            if content_mode == globals.WINDOW_SF:
                return self.statefulSetWindowColors(line)

            if content_mode == globals.WINDOW_RS:
                return self.replicaSetWindowColors(line)

            if content_mode == globals.WINDOW_DS:
                return self.daemonSetWindowColors(line)

            if content_mode == globals.WINDOW_CONTEXT:
                return self.contextWindowColors(line)

            if content_mode == globals.WINDOW_PVC:
                return self.persistentVolumeClaimsWindowColors(line)
                
            if content_mode == globals.WINDOW_PV:
                return self.persistentVolumesWindowColors(line)

            if content_mode == globals.WINDOW_DEPLOYMENT:
                return self.deploymentWindowColors(line)

            if content_mode == globals.WINDOW_SC:
                return self.storageClassWindowColors(line)

            if content_mode == globals.WINDOW_JOB:
                return self.jobWindowColors(line)

            if content_mode == globals.WINDOW_CRONJOB:
                return self.cronJobWindowColors(line)

            if content_mode == globals.WINDOW_ROLE:
                return self.roleWindowColors(line)

            if content_mode == globals.WINDOW_ROLEBINDING:
                return self.roleBindingWindowColors(line)

            if content_mode == globals.WINDOW_SA:
                return self.serviceAccountWindowColors(line)

            if content_mode == globals.WINDOW_PDB:
                return self.podDisruptionBudgetWindowColors(line)

            if content_mode == globals.WINDOW_ROUTE:
                return self.routeWindowColors(line)

            if content_mode == globals.WINDOW_INGRESS:
                return self.ingressWindowColors(line)

            if content_mode == globals.WINDOW_NODE:
                return self.nodeWindowColors(line)

            if content_mode == globals.WINDOW_CRD:
                return self.crdWindowColors(line)

            if content_mode == globals.WINDOW_NAMESPACE:
                return self.namespaceWindowColors(line)


            #if document.current_line in line:
            #    return [(NAMED_COLORS["Black"],line)]

            #unknown, yellow
            return [(NAMED_COLORS["Yellow"],line)]
            
        return get_line

class OutputAreaLexer(Lexer):
    
    def lex_document(self, document):
        #colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))
        def get_line(lineno):

            #default lexer used when search string not found or search not speficied            
            def defaultLexer(line):
                if line.find("=== ") == 0:
                    return [(NAMED_COLORS["Cyan"],line)]
                
                if line.find("TIMEOUT ") == 0:
                    return [(NAMED_COLORS["Yellow"],line)]

                #TODO: some kind of configuration for error lines
                if lowerLine.startswith("error:") or lowerLine.find(" error ") > 0 or lowerLine.find(" error") > 0 or lowerLine.find("exception: ")>0:
                    return [(NAMED_COLORS["Red"],line)]

                return [(defaultColor,line)]
            
            #default, white
            #defaultColor=NAMED_COLORS["White"]
            defaultColor="#bbbbbb"

            line = document.lines[lineno]
            lowerLine = line.lower()

            #import search string from state
            from .state import searchString
            if searchString != "":
                #TODO add case sensitivity as config option
                searchString = searchString.lower()
                
                searchStringLength = len(searchString)
                searchResultFormat = 'bg:ansibrightyellow ansiblack'
                startIndex = 0
                foundIndex = lowerLine.find(searchString,startIndex)
                formattedText = []
                if foundIndex > -1:
                    while foundIndex > -1:
                        formattedText.append((defaultColor,line[startIndex:foundIndex]))
                        #new start index is lenght of search string + found index
                        startIndex = foundIndex + searchStringLength
                        #found text
                        formattedText.append((searchResultFormat,line[foundIndex:startIndex]))
                        foundIndex = lowerLine.find(searchString,startIndex)
                else:
                    return defaultLexer(line)
                    #formattedText.append((defaultColor,line))
                if startIndex > 0:
                    #add end of the line using default format
                    formattedText.append((defaultColor,line[startIndex:]))
                return formattedText
            else:
                return defaultLexer(line)        
            # if line.find("=== ") == 0:
            #     return [(NAMED_COLORS["Cyan"],line)]
            
            # if line.find("TIMEOUT ") == 0:
            #     return [(NAMED_COLORS["Yellow"],line)]

            # #TODO: some kind of configuration for error lines
            # if lowerLine.find(" error ") > 0 or lowerLine.find("exception: ")>0:
            #     return [(NAMED_COLORS["Red"],line)]

            # return [(defaultColor,line)]
            
        return get_line

    