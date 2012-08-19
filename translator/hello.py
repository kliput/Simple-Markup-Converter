from translator.translator import Translator

class HelloTranslator(Translator):
    '''
    Translator napisany dla przypomnienia PLY
    '''
    
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)
        
    
    tokens = (
        'WORD',
    )
    
    # ciąg zwartych znaków
    t_WORD = r'[\w\~\`\!\@\#\$\%\^\&\*\(\)\-\+\[\]\{\}\:\;\"\'\<\>\?\,\.\/\|\\]+'

    t_ignore = ' \t\n'
    
#    def t_NL_ONE(self, t):
#        r'\n'
#        self.log.debug("newline one")
#    
#    def t_NL_TWO(self, t):
#        r'\n\n'
#        self.log.debug("newline two")

    def p_document(self, p):
        '''
        document    : document paragraph
        '''
        self.log.debug('document    : document paragraph')
        p[0] = p[1] + p[2]
        
    def p_document_blank(self, p):
        '''
        document    : 
        '''
        self.log.debug("document blank")
        p[0] = ''
        
    # akapit zawierający więcej elementów
    def p_paragraph(self, p):
        '''
        paragraph   : paragraph element '\\n' '\\n'
        '''
        self.log.debug('paragraph paragraph element') 
        p[0] = p[0] + p[1]
        
    # ostatni bądź jedyny element w akapicie
    def p_paragraph_last_element(self, p):
        '''
        paragraph    : element
        '''
        self.log.debug('paragraph element')
        p[0] = p[1]
        
    ## TODO element
    def p_element(self, p):
        '''
        element    : plain 
        '''
        self.log.debug('element plain')
        p[0] = p[1]
        
    def p_plain(self, p):
        '''
        plain    : plain WORD
        '''
        self.log.debug('plain WORD: %s' % p[2])
        # między dwoma ciągami znaków jest zawsze pojedyncza spacja
        p[0] = p[1] + ' ' + p[2]
        
    def p_plain_last(self, p):
        '''
        plain    : WORD
        '''
        self.log.debug('plain last word: %s' % p[1])
        p[0] = p[1]
    