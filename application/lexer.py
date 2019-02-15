from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles.named_colors import NAMED_COLORS


class PodStatusLexer(Lexer):
    
    def lex_document(self, document):
        #colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))
        def get_line(lineno):
            line = document.lines[lineno]
            #OK, green
            if "Running" in line or "Completed"  in line:
                return [(NAMED_COLORS["Green"],line)]
            #error, red
            if "CrashLoopBackOff" in line :
                return [(NAMED_COLORS["Red"],line)]
            
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

            #default, white
            #defaultColor=NAMED_COLORS["White"]
            defaultColor="#bbbbbb"
            return [(defaultColor,line)]
            
        return get_line