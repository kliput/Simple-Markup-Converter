# -*- coding: utf-8 -*-

from .translator import Translator
import re


class Txt2Tags(Translator):

    def __init__(self):
        print('Txt2Tags constructor')
        super().__init__()

    tokens = (
        'PLAIN',
    )

#    states = (
#        ('dummystat', 'inclusive'),
#    )
    
#    # literaly, ktore nie zmienia stanu
#    literals = ['@', '{', ',', '}']

    t_PLAIN = r'.*?'

#    # typ publikacji -> pierwszy token
#    def t_INITIAL_TYPE(self, t):
#        '''\w+'''
#        t.lexer.begin('idstat')
#        return t
    
    # glowne
    ## TODO nie wiem czy to potrzebne?
    def p_document(self, p):
        '''
        document    : text
        '''
        p[0] = p[1]
        self.output = p[0]
    
    def p_text(self, p):
        '''
        text    : text formatted
            | text PLAIN
        '''
        p[0] = p[1] + p[2]
    
    def p_text_empty(self, p):
        '''
        text    :
        '''
    
    def p_formatted_text(self, p):
        '''
        formatted    : bold
        '''
        
    def p_bold(self, p):
        '''
        bold    : '*' '*' text '*' '*'
        '''
    
    def p_error(self, p):
        print("syntax error in line %d: ...%s..." % (p.lineno, p.value))
