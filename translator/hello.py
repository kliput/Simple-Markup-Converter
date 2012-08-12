from translator.translator import Translator

class HelloTranslator(Translator):
    '''
    Translator napisany dla przypomnienia PLY
    '''
    
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)
        
    
    tokens = (
        'PLAIN',
        'BOLD',
    )
    
    t_PLAIN = r'(.|\n)+'
    
    t_BOLD = r'\*\*'
    
    def p_text(self, p):
        '''
        text    :    text PLAIN
                |    text bold
        '''
        self.log.debug('p_text')
        p[0] = p[1] + p[2]
    
    def p_bold(self, p):
        '''
        bold    :    BOLD text BOLD
        '''
        self.log.debug('p_bold')
        p[0] = '<b>%s</b>' % p[2]
    
    def p_text_blank(self, p):
        '''
        text    : 
        '''
        self.log.debug('p_text_blank')
        p[0] = ''
        