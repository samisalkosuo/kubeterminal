from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS
import re
import kubeterminal.globals as globals

class ResourceWindowLexer(Lexer):

    def windowColors(self,contentMode, line):        

        if contentMode == globals.WINDOW_POD:
            if "CrashLoopBackOff" in line or "Terminating" in line:
                return [(NAMED_COLORS["Red"],line)]
            if "Completed" in line:
                return [(NAMED_COLORS["GreenYellow"],line)]
            #find out running status
            #assume that line includes something like 2/2 or 1/1 or 1/3 
            #to show how many pods are running 
            if self.isRunningEqualReady(line) == False:
                return [(NAMED_COLORS["Yellow"],line)]
            #All appear to be running, if Running on line then green
            if "Running" in line:
                return [(NAMED_COLORS["Green"],line)]

        if contentMode == globals.WINDOW_CM or \
            contentMode == globals.WINDOW_SECRET or \
            contentMode == globals.WINDOW_ROUTE or \
            contentMode == globals.WINDOW_CRD or \
            contentMode == globals.WINDOW_PDB or \
            contentMode == globals.WINDOW_SA or \
            contentMode == globals.WINDOW_ROLEBINDING or \
            contentMode == globals.WINDOW_ROLE or \
            contentMode == globals.WINDOW_CRONJOB or \
            contentMode == globals.WINDOW_SC or \
            contentMode == globals.WINDOW_INGRESS \
            : 
            #default green
            return [(NAMED_COLORS["Green"],line)]

        from .state import current_namespace
        offset = 0
        if current_namespace == "all-namespaces":
            offset = 1

        #split line
        fields = line.split()
        value = None
        desiredValue = None
        if contentMode == globals.WINDOW_NAMESPACE:
            value = fields[1]
            desiredValue = "Active"
        if contentMode == globals.WINDOW_NODE:
            value = fields[1]
            desiredValue = "Ready"
        if contentMode == globals.WINDOW_PV:
            value = fields[4]
            desiredValue = "Bound"
        if contentMode == globals.WINDOW_PVC:
            value = fields[1+offset]
            desiredValue = "Bound"

        if value != None and desiredValue != None:
            return self.checkSingleField(line, value, desiredValue)

        if contentMode == globals.WINDOW_JOB or \
            contentMode == globals.WINDOW_DEPLOYMENT or \
            contentMode == globals.WINDOW_STS \
            :
            return self.checkRunningSlashReady(line)

        if contentMode == globals.WINDOW_SVC:
            if "NodePort" in line:
                return [(NAMED_COLORS["GreenYellow"],line)]
            else:
                return [(NAMED_COLORS["Green"],line)]

        array = [1,2]
        #check desired, current, etc fields
        if contentMode == globals.WINDOW_DS:
            array = [fields[1+offset],fields[2+offset],fields[3+offset],fields[4+offset],fields[5+offset]]
        if contentMode == globals.WINDOW_RS:
            array = [fields[1+offset],fields[2+offset],fields[3+offset]]

        if self.arrayValuesAreEqual(array) == True:
            return [(NAMED_COLORS["Green"],line)]

        #default/unknown yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def lex_document(self, document):
        #colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))
        def get_line(lineno):
            line = document.lines[lineno]
            #import content mode
            from .state import content_mode
            return self.windowColors(content_mode, line)
            
        return get_line

    def arrayValuesAreEqual(self,arrayOfValues):        
        checkValue = arrayOfValues[0]
        for value in arrayOfValues:
            if value != checkValue:
                return False

        return True

    def isRunningEqualReady(self, line):

        matchObj = re.search( r'([0-9]+)/([0-9]+)', line)
        rv = False
        if matchObj:
            runningNow=int(matchObj.group(1))
            runningTarget=int(matchObj.group(2))
            rv = runningNow == runningTarget
        
        return rv

    def checkRunningSlashReady(self,line):

        if self.isRunningEqualReady(line) == True:
                return [(NAMED_COLORS["Green"],line)]

        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]

    def checkSingleField(self,line,value,desiredValue):
        #if value equals desiredValue return Green line
        #else return yellow
        if value == desiredValue:
            return [(NAMED_COLORS["Green"],line)]
        #default yellow
        return [(NAMED_COLORS["Yellow"],line)]


class OutputWindowLexer(Lexer):
    
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

    