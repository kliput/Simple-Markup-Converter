# -*- coding: utf-8 -*-

from .translator import Translator
import logging

class PassTranslator(Translator):
    '''
    Pusty translator, który zwraca ten sam tekst, który otrzymał.
    '''
    
    log = logging.getLogger(__name__)

    output = ''

    def __init__(self):
        self.log.debug('PassTranslator constructor')
        super().__init__()
    

    tokens = (
        'PLAIN_TEXT',
    )
    
    t_PLAIN_TEXT = r'(.|\n)+'
    

    def p_text(self, p):
        '''
        text    : PLAIN_TEXT
        '''
        p[0] = p[1]
        self.output = p[0]
