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
            line = document.lines[lineno]
            #OK, green
            
            if line.find("=== ") == 0:
                return [(NAMED_COLORS["Cyan"],line)]
            
            if line.find("TIMEOUT ") == 0:
                return [(NAMED_COLORS["Yellow"],line)]

            lowerLine = line.lower()
            #TODO: some kind of configuration for error lines
            if lowerLine.find(" error ") > 0 or lowerLine.find("exception: ")>0:
                return [(NAMED_COLORS["Red"],line)]

            #default, white
            #defaultColor=NAMED_COLORS["White"]
            defaultColor="#bbbbbb"
            return [(defaultColor,line)]
            
        return get_line