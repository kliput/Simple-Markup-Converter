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
        'PAREND',
        'NEWLINE',
    )
    
    # ciąg zwartych znaków
    t_WORD = r'[\w\~\`\!\@\#\$\%\^\&\*\(\)\-\+\[\]\{\}\:\;\"\'\<\>\?\,\.\/\|\\]+\n??'

    t_NEWLINE = '\\n'

    t_PAREND = '\\n{2,}'

    t_ignore = ' \t'
    
#    def t_NL_ONE(self, t):
#        r'\n'
#        self.log.debug("newline one")
#    
#    def t_NL_TWO(self, t):
#        r'\n\n'
#        self.log.debug("newline two")

    def p_document_multi(self, p):
        '''
        document    : document PAREND paragraph
        '''
        self.log.debug('document: document (%s)  PAREND paragraph (%s)' % (p[1], p[3]))
        p[0] = '%s <p>%s</p>' % (p[1], p[3])
    
    def p_document(self, p):
        '''
        document    : paragraph
        '''
        self.log.debug('document: paragraph (%s)' % (p[1]))
        p[0] = '<p>%s</p>' % p[1]
    
    # dokument może być w ogóle pusty
    def p_document_blank(self, p):
        '''
        document    : 
        '''
        self.log.debug("(document blank)")
        p[0] = ''
        
    # akapit zawierający więcej elementów
    def p_paragraph(self, p):
        '''
        paragraph   : paragraph element
        '''
        self.log.debug('paragraph: paragraph (%s) element (%s)' % (p[1], p[2])) 
        p[0] = p[1] + p[2]
        
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_wnl(self, p):
        '''
        paragraph   : paragraph NEWLINE element
        '''
        self.log.debug('paragraph: paragraph (%s) NEWLINE element (%s)' % (p[1], p[3])) 
        p[0] = p[1] + '\n' + p[3]
        
    # ostatni bądź jedyny element w akapicie
    def p_paragraph_last_element(self, p):
        '''
        paragraph    : element
        '''
        self.log.debug('paragraph: element (%s)' % (p[1]))
        p[0] = p[1]    
        
    ## TODO element
    def p_element(self, p):
        '''
        element    : plain 
        '''
        self.log.debug('element: plain (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_plain(self, p):
        '''
        plain    : plain WORD
        '''
        self.log.debug('plain: plain (%s) WORD (%s)' % (p[1], p[2]))
        # między dwoma ciągami znaków jest zawsze pojedyncza spacja
        p[0] = p[1] + ' ' + p[2]
        
    def p_plain_last(self, p):
        '''
        plain    : WORD
        '''
        self.log.debug('plain: WORD (%s)' % p[1])
        p[0] = p[1]
    
