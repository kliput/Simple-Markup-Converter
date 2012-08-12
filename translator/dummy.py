# -*- coding: utf-8 -*-

from .translator import Translator

class PassTranslator(Translator):
    '''
    Pusty translator, który zwraca ten sam tekst, który otrzymał.
    '''
    
    output = ''

    def __init__(self):
        super().__init__()
        self.log.debug('PassTranslator constructor')
    

    tokens = (
        'PLAIN_TEXT',
    )
    
    t_PLAIN_TEXT = r'(.|\n)+'
    

    def p_text(self, p):
        '''
        text    : PLAIN_TEXT
        '''
        p[0] = p[1]
