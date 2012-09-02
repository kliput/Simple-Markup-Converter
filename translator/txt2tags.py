from translator.translator import Translator

class Txt2TagsToXML(Translator):
    '''
    Translator txt2tags -> XML (języka wewnętrznego)
    '''
    
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)
        
    
    tokens = (
        'PAREND',
        'NEWLINE',
#        'BOLD_START',
#        'BOLD_END',
        'WORD',
        'BOLD',
    )
    
    t_ignore = ' \t'
    
#    char_set = r'\w\~\`\!\@\#\$\%\^\&\*\(\)\-\+\[\]\{\}\:\;\"\'\<\>\?\,\.\/\|\\'
    
    # ciąg zwartych znaków
    t_WORD = r'[^\s]+'
    
    def t_BOLD_START(self, t):
        r'\*\*(?=[^\s])'
        self.log.debug('BOLD START token: ' + t.value)
        return t

    def t_BOLD_END(self, t):
        r'(?<=[^\s])\*\*'
#        r'\**\*\*'
        self.log.debug('BOLD END token: ' + t.value)
        return t
    
    # TODO jest to pewne rozwiązanie, ale w kontekście całości - źle
#    def t_BOLD(self, t):
#        r'\*\*([^\s](|.*?[^\s])\**)\*\*'
#        self.log.debug('BOLD TOKEN: ' + t.value)
#        t.value = '<b>%s</b>' % t.value
#        return t
    
#    def t_WORD(self, t):
#        r'[^\s]+(?<!\*)'
#        self.log.debug('WORD token: ' + t.value)
#        return t

    # 1 znak nowej linii - może pojawić się w ramach akapitu
    t_NEWLINE = '\\n'

    # 2 lub więcej znaków nowej linii - oddziela akapit
    t_PAREND = '\\n{2,}'
    
#    t_BOLD_START = r'\*\*(?=[^\s])' 
#    t_BOLD_END = r'(?<=[^\s])\*\*'
    
    
#    precedence = (
#        ('right', 'BOLD_END'),
#    )
    
    # dokument z wieloma akapitami
    def p_document_multi(self, p):
        '''
        document    : document PAREND paragraph
        '''
        self.log.debug('document: document (%s)  PAREND paragraph (%s)' % (p[1], p[3]))
        p[0] = p[1] + ' ' + p[3]
    
    # dokument z jednym akapitem, bądź pierwszy akapit
    def p_document(self, p):
        '''
        document    : paragraph
        '''
        self.log.debug('document: paragraph (%s)' % (p[1]))
        p[0] = p[1]
    
#    # dokument może być w ogóle pusty
#    def p_document_blank(self, p):
#        '''
#        document    : 
#        '''
#        self.log.debug("(document blank)")
#        p[0] = ''
    
    def p_paragraph(self, p):
        '''
        paragraph    : paragraph_content
        '''
        p[0] = '<p>%s</p>' % p[1]
        
    def p_paragraph_blank(self, p):
        '''
        paragraph    : 
        '''
        p[0] = ''
        
#    def p_paragraph_content_blank(self, p):
#        '''
#        paragraph_content    :
#        '''
#        p[0] = ''
    
    # akapit zawierający więcej elementów
    def p_paragraph_content(self, p):
        '''
        paragraph_content   : paragraph_content element
        '''
        self.log.debug('paragraph_content: paragraph_content (%s) element (%s)' % (p[1], p[2])) 
        p[0] = p[1] + p[2]
        
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_wnl(self, p):
        '''
        paragraph_content   : paragraph_content element NEWLINE
        '''
        self.log.debug('paragraph_content: paragraph_content (%s) element (%s) NEWLINE' % (p[1], p[2])) 
        p[0] = p[1] + p[2] + '\n'

    # TODO co to jest?
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_blank(self, p):
        '''
        paragraph_content   : 
        '''
        p[0] = ''
        
    ## TODO element
    def p_element(self, p):
        '''
        element    : plain 
                    | BOLD
        '''
        self.log.debug('element: (...) (%s)' % (p[1]))
        p[0] = p[1]
        
#    def p_bold(self, p):
#        '''
#        bold    : BOLD_START plain BOLD_END
#        '''
#        p[0] = '<b>%s</b>' % p[2]
        
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
    
