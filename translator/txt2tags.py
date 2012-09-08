from translator.translator import Translator
import re

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
        'BOLD_S',
        'BOLD_E',
        'BOLD_E_I',
        'BOLD_E_U',
        'ITALIC_S',
        'ITALIC_E',
        'ITALIC_E_B',
        'ITALIC_E_U',
        'UNDERLINE_S',
        'UNDERLINE_E',
        'UNDERLINE_E_B',
        'UNDERLINE_E_I',
        'WORD',
    )
    
    states = (
        ('bs', 'inclusive'), # bold started
        ('is', 'inclusive'), # italic started
        ('us', 'inclusive'), # underline started
        ('tagend', 'exclusive'), # gotowość do parsowana taga zamykającego formatowanie
    )
    
    t_ANY_ignore = ' \t'
    
    # ------ tagi startujące formatowanie ------
    
    # Te tagi powinny być dostępne we wszystkich trybach oprócz tagend. 
    
    # Znacznik rozpoczynający pogrubienie: **<znak>
    # Może być wykryte tylko w stanie, gdy nie rozpoczęliśmy znacznika bold
    # (w obecnym zagnieżdżeniu)
    # TODO dodawać możliwe wszystkie stany inclusive
    def t_INITIAL_is_us_BOLD_S(self, t):
        r'\*\*(?=[^\s])'
        # dorzucenie stanu otwartego bold
        t.lexer.push_state('bs')
        self.log.debug('BOLD_S token: ' + t.value)
        return t
    
    # znacznik rozpoczynający kursywę: //<znak>
    # TODO dodawać możliwe wszystkie stany inclusive
    def t_INITIAL_bs_us_ITALIC_S(self, t):
        r'\/\/(?=[^\s])'
        # dorzucenie stanu otwartego italic
        t.lexer.push_state('is')
        self.log.debug('ITALIC_S token: ' + t.value)
        return t
    
    def t_INITIAL_bs_is_UNDERLINE_S(self, t):
        r'\_\_(?=[^\s])'
        self.log.debug('>>')
        t.lexer.push_state('us')
        return t
    
    # ------ tagi kończące formatowanie ------
    
    # --- BOLD ---
    
    # koniec bold, ale także koniec znacznika //
    # **//
    def t_tagend_BOLD_E_I(self, t):
        r'\*\*(?=\/\/)'
        self.log.debug('t_be_BOLD_E_I: ' + t.value)
        return t

    # **__
    def t_tagend_BOLD_E_U(self, t):
        r'\*\*(?=\_\_)'
        return t
    
    # Znacznik kończący bold, musi go poprzedzać jakiś znak.
    # Nie można wykonać "positive lookbehind" gdyż poprzedni znak należy
    # do jakiegoś innego tokena. W tym celu używa się flagi format['bold'].  
    def t_tagend_BOLD_E(self, t):
        r'\*\*'
        # zdjęcie stanu be - koniec bold
        t.lexer.pop_state()
        self.log.debug('t_be_BOLD_E: ' + t.value)
        return t

    # --- ITALIC ---

    # //**
    def t_tagend_ITALIC_E_B(self, t):
        r'\/\/(?=\*\*)'
        self.log.debug('t_ITALIC_E_B: ' + t.value)
        return t

    # //__
    def t_tagend_ITALIC_E_U(self, t):
        r'\/\/(?=\_\_)'
        return t

    # Analogicznie do t_tagend_BOLD_E
    def t_tagend_ITALIC_E(self, t):
        r'\/\/'
        # zdjęcie stanu ie - koniec italic
        t.lexer.pop_state()
        self.log.debug('t_ie_ITALIC_E: ' + t.value)
        return t
    
    # --- UNDERLINE ---
    
    # __**
    def t_tagend_UNDERLINE_E_B(self, t):
        r'\_\_(?=\*\*)'
        return t

    # //__
    def t_tagend_UNDERLINE_E_I(self, t):
        r'\_\_(?=\/\/)'
        return t

    # Analogicznie do t_tagend_BOLD_E
    def t_tagend_UNDERLINE_E(self, t):
        r'\_\_'
        t.lexer.pop_state()
        return t

    # --- WORD ---

    # Szukamy pierwszego wystąpienia zamykającego taga, 
    # który jest poprzedzony przynajmniej jednym dowolnym znakiem.
    # Znaków taga nie bierzemy do wyniku wyrażenia regularnego
    # - będą użyte przy pobraniu taga zamykającego.
    def t_bs_is_us_WORD(self, t):
        r'[^\s]+?(?=(\*\*)|(\/\/)|(\_\_))'
        # lexer gotowy na pobranie znaków zamykających bold
        t.lexer.begin('tagend')
        self.log.debug('WORD ending tag token: ' + t.value)
        return t

    # słowo wykrywane we wszystkich trybach
    def t_WORD(self, t):
        r'[^\s]+'
#        if t.lexer.current_state == 'tagend':
#            t.lexer.pop_state()
        self.log.debug('WORD normal token: ' + t.value);
        return t

    # 1 znak nowej linii - może pojawić się w ramach akapitu
    t_NEWLINE = '\\n'

    # 2 lub więcej znaków nowej linii - oddziela akapit
    t_PAREND = '\\n{2,}'
    
        
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
        self.log.debug('par %s' % p[1])
        p[0] = '<p>%s</p>' % p[1]
        
    def p_paragraph_blank(self, p):
        '''
        paragraph    : 
        '''
        self.log.debug('par BLANK')
        p[0] = ''
        
    # akapit zawierający więcej elementów
    def p_paragraph_content(self, p):
        '''
        paragraph_content   : paragraph_content line_content
        '''
        p[0] = p[1] + p[2]
        
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_wnl(self, p):
        '''
        paragraph_content   : paragraph_content line_content NEWLINE
        '''
        p[0] = p[1] + p[2] + '\n'

    # TODO co to jest?
    # akapit zawierający więcej elementów przedzielone pojedynczym znakiem nowej linii
    def p_paragraph_content_blank(self, p):
        '''
        paragraph_content   : 
        '''
        self.log.debug('line_content BLANK')
        p[0] = ''
        
    # zawartość pojedynczej linii (wiele elementów)
    def p_line_content(self, p):
        '''
        line_content   : line_content element
        '''
        
        p[0] = p[1] + ' ' + p[2]
    
    # zawartość pojedynczej linii - ostatni element
    def p_line_content_blank(self, p):
        '''
        line_content    : element
        '''
        self.log.debug('lc (single) %s' % (p[1]))
        p[0] = p[1]
        
    def p_element(self, p):
        '''
        element    : plain 
                    | bold
                    | italic
                    | underline
        '''
        self.log.debug('element: (...) (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_bold(self, p):
        '''
        bold    : BOLD_S line_content bold_end
        '''
        p[0] = '<b>%s</b>' % p[2]
        
    def p_bold_end(self, p):
        '''
        bold_end    : BOLD_E
                    | BOLD_E_I
                    | BOLD_E_U
        '''

    def p_italic(self, p):
        '''
        italic    : ITALIC_S line_content italic_end
        '''
        p[0] = '<i>%s</i>' % p[2]
        
    def p_italic_end(self, p):
        '''
        italic_end    : ITALIC_E
                        | ITALIC_E_B
                        | ITALIC_E_U
        '''
        p[0] = p[1]
        
    def p_underline(self, p):
        '''
        underline    : UNDERLINE_S line_content underline_end
        '''
        p[0] = '<u>%s</u>' % p[2]
        
    def p_underline_end(self, p):
        '''
        underline_end    : UNDERLINE_E
                        |    UNDERLINE_E_B
                        |    UNDERLINE_E_I
        '''
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
