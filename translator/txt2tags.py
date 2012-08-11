# -*- coding: utf-8 -*-

from .translator import Translator
import logging

#import re

class Txt2TagsOutput(Translator):
    pass

class Txt2TagsInput(Translator):

    log = logging.getLogger(__name__)

    output = ''

    def __init__(self):
        self.log.debug('Txt2Tags constructor')
        super().__init__()
    

    tokens = (
        'PLAIN_TEXT',
    )
    
#    literals = ['\n']

    t_PLAIN_TEXT = r'(.|\n)+'


    def p_text(self, p):
        '''
        text    : PLAIN_TEXT
        '''
        p[0] = p[1]
        self.output = p[0]
