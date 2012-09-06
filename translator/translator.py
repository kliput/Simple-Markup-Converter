# -*- coding: utf-8 -*-

import logging
import ply.lex as lex
import ply.yacc as yacc

class Translator(object):
    '''
    Klasa bazowa dla wszystkich translatorów
    
    Zawiera m.in. pola:
     my_lex   - lexer
     my_yacc  - parser
     log      - logger
    '''
    
    tokens = ()
    precedence = ()
    # TODO: przełącznik na debug
    debug = 0
        
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Translator constructor')
        self.my_lex = lex.lex(module=self, debug=self.debug)
        self.my_yacc = yacc.yacc(module=self, debug=self.debug)
    
    def run(self, text):
        if text == '':
            return ''
        else:
            return self.my_yacc.parse(input=text, lexer=self.my_lex, debug=self.debug)
