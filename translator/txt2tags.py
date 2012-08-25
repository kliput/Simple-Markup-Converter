from translator.translator import Translator

class Txt2TagsToXML(Translator):
    '''
    Translator txt2tags -> XML (języka wewnętrznego)
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

    # 1 znak nowej linii - ignorowany przy końcowym formatowaniu
    t_NEWLINE = '\\n'

    # 2 lub więcej znaków nowej linii - oddziela akapit
    t_PAREND = '\\n{2,}'

    t_ignore = ' \t'
    
    # dokument z wieloma akapitami
    def p_document_multi(self, p):
        '''
        document    : document PAREND paragraph
        '''
        self.log.debug('document: document (%s)  PAREND paragraph (%s)' % (p[1], p[3]))
#        p[0] = '%s <p>%s</p>' % (p[1], p[3])
        p[0] = p[1] + ' ' + p[3]
    
    # dokument z jednym akapitem, bądź pierwszy akapit
    def p_document(self, p):
        '''
        document    : paragraph
        '''
        self.log.debug('document: paragraph (%s)' % (p[1]))
#        p[0] = '<p>%s</p>' % p[1]
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
        paragraph_content   : paragraph_content NEWLINE element
        '''
        self.log.debug('paragraph_content: paragraph_content (%s) NEWLINE element (%s)' % (p[1], p[3])) 
        p[0] = p[1] + '\n' + p[3]
        
    # ostatni bądź jedyny element w akapicie
    def p_paragraph_content_last_element(self, p):
        '''
        paragraph_content    : element
        '''
        self.log.debug('paragraph_content: element (%s)' % (p[1]))
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
    
