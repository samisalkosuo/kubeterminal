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

    