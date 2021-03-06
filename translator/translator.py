# -*- coding: utf-8 -*-

import logging
import ply.lex as lex
import ply.yacc as yacc
import re

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
        self.my_lex = lex.lex(module=self, debug=self.debug, reflags=re.MULTILINE)
        self.my_yacc = yacc.yacc(module=self, debug=self.debug)
    
    def run(self, text):
        if text == '':
            return ''
        else:
            # dodanie nowej linii i końca akapitu na końcu pliku - upraszcza gramatyki
            text = text + '\n\n\n'
            
#            if self.debug == 0:
#                print('Parsing:')
#                print('--------')
#                print(text)
#                print('--------')
                          
            return self.my_yacc.parse(input=text, lexer=self.my_lex, debug=self.debug)
