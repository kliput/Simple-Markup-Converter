import ply.lex as lex
import ply.yacc as yacc

class Translator(object):
    tokens = ()
    precedence = ()
    debug = 0
    
    def __init__(self, **kw):
        self.my_lex = lex.lex(module=self, debug=self.debug)
        self.my_yacc = yacc.yacc(module=self, debug=self.debug)
    
    def run(self, text):
        self.my_yacc.parse(input=text, lexer=self.my_lex, debug=self.debug)
        return self.output
