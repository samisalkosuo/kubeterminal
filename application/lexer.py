from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS


class PodStatusLexer(Lexer):
    
    def lex_document(self, document):
        #colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))
        def get_line(lineno):
            line = document.lines[lineno]

            #error, red
            if "CrashLoopBackOff" in line or "Terminating" in line:
                return [(NAMED_COLORS["Red"],line)]

            if "Completed" in line:
                return [(NAMED_COLORS["GreenYellow"],line)]

            # if Running and 0/something => GreenYellow
            if "Running" in line and "0/" in line:
                return [(NAMED_COLORS["Yellow"],line)]

            if "0/" in line:
                return [(NAMED_COLORS["Yellow"],line)]

            #OK, green
            if "Running" in line:
                return [(NAMED_COLORS["Green"],line)]

            
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
                if lowerLine.find(" error ") > 0 or lowerLine.find(" error") > 0 or lowerLine.find("exception: ")>0:
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

    