from translator.translator import Translator

class Txt2TagsToXML(Translator):
    '''
    Translator txt2tags -> XML (języka wewnętrznego)
    '''
    
    # Mapa otwartych znaczników formatowania.
    # Znaczniki tego samego typu nie mogą się zagnieżdżać.
    format = {
              'bold': False, # pojawił się początek bold
              }
    
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)
        
    
    tokens = (
        'PAREND',
        'NEWLINE',
        'BOLD_S',
        'BOLD_E',
        'WORD',
    )
    
    states = (
        ('bs', 'inclusive'), # bold started
        ('be', 'exclusive'), # bold end - można wykryć zamykanie bold
    )
    
    t_ANY_ignore = ' \t'
    
    # znacznik rozpoczynający pogrubienie: **<znak>
    def t_BOLD_S(self, t):
        r'\*\*(?=[^\s])'
        # sprawdzenie, czy już został otwarty znacznik **
        # można używać stosu stanów, ale to bardziej skomplikowane
        if not self.format['bold']:
            # jeśli nie - ustawienie tej flagi oraz stanu
            self.format['bold'] = True
            t.lexer.push_state('bs')
            # i normalne zwrócenie tokenu
            self.log.debug('BOLD_S token: ' + t.value)
            return t
        else:
            # jeśli tak - pominięcie go
            self.log.debug('BOLD_S skip: ' + t.value)
            
    
    # Znacznik kończący bold, musi go poprzedzać jakiś znak.
    # Nie można wykonać "positive lookbehind" gdyż poprzedni znak należy
    # do jakiegoś innego tokena. W tym celu używa się flagi format['bold'].  
    def t_be_BOLD_E(self, t):
        r'\*\*'
        # zdjęcie stanu be - koniec bold
        t.lexer.pop_state()
        # koniec bloku bold - można parsować kolejny początek bold
        self.format['bold'] = False
        self.log.debug('t_be_BOLD_E: ' + t.value)
        return t

    # Szukamy pierwszego wystąpienia podwójnych gwiazdek, 
    # które są poprzedzone przynajmniej jednym dowolnym znakiem.
    # Gwiazdek nie bierzemy do wyniku wyrażenia regularnego
    # - będą użyte przy pobraniu taga zamykającego.
    def t_bs_WORD(self, t):
        r'[^\s]+?(?=\*\*)'
        # lexer gotowy na pobranie znaków zamykających bold
        t.lexer.begin('be')
        self.log.debug('WORD ending bold token: ' + t.value)
        return t

    # słowo wykrywane we wszystkich trybach
    def t_WORD(self, t):
        r'[^\s]+'
        self.log.debug('WORD normal token: ' + t.value);
        return t

    # 1 znak nowej linii - może pojawić się w ramach akapitu
    t_NEWLINE = '\\n'

    # 2 lub więcej znaków nowej linii - oddziela akapit
    t_PAREND = '\\n{2,}'
    
#    t_BOLD_START = r'\*\*(?=[^\s])' 
#    t_BOLD_END = r'(?<=[^\s])\*\*'
    
        
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
        p[0] = p[1] + ' ' + p[2]
        
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_wnl(self, p):
        '''
        paragraph_content   : paragraph_content element NEWLINE
        '''
        self.log.debug('paragraph_content: paragraph_content (%s) element (%s) NEWLINE' % (p[1], p[2])) 
        p[0] = p[1] + ' ' + p[2] + '\n'

    # TODO co to jest?
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_blank(self, p):
        '''
        paragraph_content   : 
        '''
        p[0] = ''
        
    def p_element(self, p):
        '''
        element    : plain 
                    | bold
        '''
        self.log.debug('element: (...) (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_bold(self, p):
        '''
        bold    : BOLD_S plain BOLD_E
        '''
        p[0] = '<b>%s</b>' % p[2]
        
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
    
