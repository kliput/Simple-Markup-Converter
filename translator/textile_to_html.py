from translator.translator import Translator
import re

class TextileToHTML(Translator):
    '''
    Translator Textile -> HTML (języka wewnętrznego)
    '''
        
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)
        
    
    tokens = (
        'PAREND',
        'NEWLINE',
        'BOLD_S',
        'BOLD_E',
        'BOLD_E_E',
        'ITALIC_S',
        'ITALIC_E',
        'ITALIC_E_E',
        'UNDERLINE_S',
        'UNDERLINE_E',
        'UNDERLINE_E_E',
        'WORD',
        'HEADING_S',
        'HEADING_E',
        'BULLET1',
        'BULLET2',
        'NUM_BULLET1',
        'NUM_BULLET2',
    )
    
    states = (
        ('bs', 'inclusive'), # bold started
        ('is', 'inclusive'), # italic started
        ('us', 'inclusive'), # underline started
        ('tagend', 'exclusive'), # gotowość do parsowana taga zamykającego formatowanie
        ('head1', 'exclusive'), # nagłówek
        ('head2', 'exclusive'), # nagłówek
        ('head3', 'exclusive'), # nagłówek
        ('head4', 'exclusive'), # nagłówek
        ('head5', 'exclusive'), # nagłówek
    )
    
#    t_ignore = r'\ \t'
    
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
        r'\_\_(?=[^\s])'
        # dorzucenie stanu otwartego italic
        t.lexer.push_state('is')
        self.log.debug('ITALIC_S token: ' + t.value)
        return t
    
    def t_INITIAL_bs_is_UNDERLINE_S(self, t):
        r'\+(?=[^\s])'
        t.lexer.push_state('us')
        self.log.debug('UNDERLINE_S token: ' + t.value)
        return t
    
    # ------ tagi kończące formatowanie ------
    
    # --- BOLD ---
    
    # koniec bold, ale także koniec innego znacznika 
    # **// **__
    def t_tagend_BOLD_E_E(self, t):
        r'\*\*(?=\/\/|\_\_)'
        self.log.debug('t_be_BOLD_E_E: ' + t.value)
        t.lexer.pop_state() # tag end
        t.lexer.pop_state() # tag start
        t.lexer.push_state('tagend')
        return t

    # Znacznik kończący bold, musi go poprzedzać jakiś znak.
    # Nie można wykonać "positive lookbehind" gdyż poprzedni znak należy
    # do jakiegoś innego tokena. W tym celu używa się flagi format['bold'].  
    def t_tagend_BOLD_E(self, t):
        r'\*\*'
        self.log.debug('**<- ' + str(t.lexer.lexstatestack))
        # zdjęcie stanu tagend - koniec bold
        t.lexer.pop_state()
        t.lexer.pop_state() # tag start
        self.log.debug('t_be_BOLD_E: ' + t.value)
        return t

    # --- ITALIC ---

    # //__ //**
    def t_tagend_ITALIC_E_E(self, t):
        r'\_\_(?=\+|\*\*)'
        t.lexer.pop_state() # tag end
        t.lexer.pop_state() # tag start
        t.lexer.push_state('tagend')
        return t

    # Analogicznie do t_tagend_BOLD_E
    def t_tagend_ITALIC_E(self, t):
        r'\_\_'
        # zdjęcie stanu ie - koniec italic
        t.lexer.pop_state()
        t.lexer.pop_state() # tag start
        self.log.debug('t_ie_ITALIC_E: ' + t.value)
        return t
    
    # --- UNDERLINE ---

    # +// +**
    def t_tagend_UNDERLINE_E_E(self, t):
        r'\+(?=\_\_|\*\*)'
        t.lexer.pop_state() # tag end
        t.lexer.pop_state() # tag start
        t.lexer.push_state('tagend')
        return t

    # Analogicznie do t_tagend_BOLD_E
    def t_tagend_UNDERLINE_E(self, t):
        r'\+'
        t.lexer.pop_state()
        t.lexer.pop_state()
        return t

    # --- HEADING ---

    def t_HEADING_S(self, t):
        r'={1,5}'
        lvl = t.value.count('=')
        t.lexer.push_state('head%s' % str(lvl))
        t.value = '<h%s>' % str(lvl)
        self.log.debug('H>')
        return t
    
    def t_head1_HEADING_E(self, t):
        r'='
        t.lexer.pop_state()
        t.value = '</h1>'
        self.log.debug('<H1')
        return t

    def t_head2_HEADING_E(self, t):
        r'=='
        t.lexer.pop_state()
        t.value = '</h2>'
        self.log.debug('<H2')
        return t

    def t_head3_HEADING_E(self, t):
        r'==='
        t.lexer.pop_state()
        t.value = '</h3>'
        self.log.debug('<H3')
        return t

    def t_head4_HEADING_E(self, t):
        r'===='
        t.lexer.pop_state()
        t.value = '</h4>'
        self.log.debug('<H4')
        return t
    
    def t_head5_HEADING_E(self, t):
        r'====='
        t.lexer.pop_state()
        t.value = '</h5>'
        self.log.debug('<H5')
        return t

    # --- WYPUNKTOWANIE ---
    
    # wg specyfikacji po - musi wystąpić dokładnie jedna spacja po -
    def t_INITIAL_BULLET1(self, t):
        r'^-\ (?=\S)'
        self.log.debug('Bullet: [%s]' % (t.value))
        return t
    
    # drugi poziom wypunktowania
    def t_INITIAL_BULLET2(self, t):
        r'^(\ )+-\ (?=\S)'
        self.log.debug('Bullet II: [%s]' % (t.value))
        return t
    
    # wg specyfikacji po - musi wystąpić dokładnie jedna spacja po -
    def t_INITIAL_NUM_BULLET1(self, t):
        r'^\+\ (?=\S)'
        self.log.debug('Num bullet: [%s]' % (t.value))
        return t
    
    # drugi poziom wypunktowania
    def t_INITIAL_NUM_BULLET2(self, t):
        r'^(\ )+\+\ (?=\S)'
        self.log.debug('Num bullet II: [%s]' % (t.value))
        return t


    # --- WORD ---

    # Szukamy pierwszego wystąpienia zamykającego taga, 
    # który jest poprzedzony przynajmniej jednym dowolnym znakiem.
    # Znaków taga nie bierzemy do wyniku wyrażenia regularnego
    # - będą użyte przy pobraniu taga zamykającego.
    def t_bs_is_us_WORD(self, t):
        r'[^\s]+?(?=(\*\*)|(\+)|(\_\_))'
        # lexer gotowy na pobranie znaków zamykających bold
        t.lexer.push_state('tagend')
        self.log.debug('WORD ending tag token: ' + t.value)
        return t

    # Ostatnie słowo w nagłówku przed =
    def t_head_WORD(self, t):
        r'[^\s]+(?=\=)'
        self.log.debug('head WORD token: ' + t.value)
        return t

    # Słowo wykrywane we wszystkich trybach
    def t_ANY_WORD(self, t):
        r'[^\s]+'
        self.log.debug('WORD normal token: ' + t.value);
        return t

    # --- NOWE LINIE

    # 1 znak nowej linii - może pojawić się w ramach akapitu
    t_NEWLINE = '\\n'

    # 2 lub więcej znaków nowej linii - oddziela akapit
    t_PAREND = '(\\n\\s*){2,}'
    
    def t_ANY_WHITESPACE(self, t):
        r'[ \t\r\f\v]+'
        self.log.debug('whitespace')
    
    # ========================    
    # PARSER    
    # ========================    
    
    # === document ===
    
    # Dokument z wieloma akapitami
    def p_document_multi(self, p):
        '''
        document    : document block
        '''
        self.log.debug('document: document (%s) block (%s)' % (p[1], p[2]))
        p[0] = p[1] + p[2]
    
    def p_document_single(self, p):
        '''
        document    : block
        '''
        self.log.debug('document: block (%s)' % (p[1]))
        p[0] =  p[1]
    
    # blok: różne
    def p_block(self, p):
        '''
        block    : heading
                    | list1
                    | enum1
        '''
        self.log.debug('block: %s' % (p[1]))
        p[0] = p[1]

    
    # akapit oddzielony od dołu
    def p_block_par(self, p):
        '''
        block    : paragraph PAREND
        '''
        self.log.debug('block: par %s' % (p[1]))
        p[0] = '<p>%s</p>' % (p[1])

    # akapit, po którym od razu następuje nagłówek
    def p_block_par_head(self, p):
        '''
        block    : paragraph heading
                | paragraph list1
                | paragraph enum1
        '''
        self.log.debug('block: par (%s) other (%s)' %(p[1], p[2]))
        p[0] = '<p>%s</p>\n%s' % (p[1], p[2])

    # === lista ===
    
    # Opakowanie listy w tag <ul>
    # Rozróżnienie I i II stopienia listy
    def p_list(self, p):
        '''
        list1    : list_pos1
        list2    : list_pos2
        '''
        p[0] = '<ul>%s</ul>' % (p[1])

    # Pozycja listy.
    # Dla I poziomu: albo kolejna pozycja zwykła, albo zagnieżdżona lista
    # Dla II poziomu: tylko kolejna pozycja zwykła
    def p_list_pos(self, p):
        '''
        list_pos1    : list_pos1 list_content1
                        | list_pos1 list2
                        | list_pos1 enum2
        list_pos2    : list_pos2 list_content2
        '''
        p[0] = '%s\n%s' % (p[1], p[2])

    # Pojedyncza pozycja listy, podobnie jak w p_list_pos.
    def p_list_pos_single(self, p):
        '''
        list_pos1    : list_content1
                        | list2
                        | enum2
        list_pos2    : list_content2
        '''
        p[0] = p[1]

    # Zwykła zawartość pozycji listy: punkt odpowiedniego poziomu i treść
    def p_list_content(self, p):
        '''
        list_content1    : BULLET1 paragraph
        list_content2    : BULLET2 paragraph
        '''
        p[0] = '<li>%s</li>' % (p[2])

    # === lista numerowana ===
    
    # Opakowanie enumy numerowanej w tag <ol>
    # Rozróżnienie I i II stopienia enumy
    def p_enum(self, p):
        '''
        enum1    : enum_pos1
        enum2    : enum_pos2
        '''
        p[0] = '<ol>%s</ol>' % (p[1])

    # Pozycja enumy.
    # Dla I poziomu: albo kolejna pozycja zwykła, albo zagnieżdżona enuma
    # Dla II poziomu: tylko kolejna pozycja zwykła
    def p_enum_pos(self, p):
        '''
        enum_pos1    : enum_pos1 enum_content1
                        | enum_pos1 enum2
                        | enum_pos1 list2
        enum_pos2    : enum_pos2 enum_content2
        '''
        p[0] = '%s\n%s' % (p[1], p[2])

    # Pojedyncza pozycja enumy, podobnie jak w p_enum_pos.
    def p_enum_pos_single(self, p):
        '''
        enum_pos1    : enum_content1
                        | enum2
                        | list2
        enum_pos2    : enum_content2
        '''
        p[0] = p[1]

    # Zwykła zawartość pozycji enumy: punkt odpowiedniego poziomu i treść
    def p_enum_content(self, p):
        '''
        enum_content1    : NUM_BULLET1 paragraph
        enum_content2    : NUM_BULLET2 paragraph
        '''
        p[0] = '<li>%s</li>' % (p[2])



    # === paragraph ===

    # Zawartość akapitu
    def p_paragraph(self, p):
        '''
        paragraph   : line_content
        '''
        self.log.debug('pc: lc %s' % (p[1]))
        p[0] = p[1]
        
    # Zawartość akapitu ze znakami nowej linii wewnątrz
    def p_paragraph_wnl(self, p):
        '''
        paragraph   : paragraph NEWLINE line_content
        '''
        self.log.debug('pc: pc %s NL lc %s' % (p[1], p[3]))
        p[0] = p[1] + '\n' + p[3]
        
    # Zawartość pojedynczej linii (wiele elementów)
    def p_line_content(self, p):
        '''
        line_content   : line_content element
        '''
        self.log.debug('lc: lc %s element %s' % (p[1], p[2]))
        p[0] = p[1] + ' ' + p[2]
    
    # Zawartość pojedynczej linii - jedyny, bądź pierwszy element
    def p_line_content_single(self, p):
        '''
        line_content    : element
        '''
        self.log.debug('lc (single) %s' % (p[1]))
        p[0] = p[1]
        
    # Pusta linia - może pojawić się na końcu pliku
    def p_line_content_blank(self, p):
        '''
        line_content    : 
        '''
        self.log.debug('lc BLANK')
        p[0] = ''
        
    
    def p_heading(self, p):
        '''
        heading    : HEADING_S plain HEADING_E
        '''
        p[0] = '%s%s%s' % (p[1], p[2], p[3])
            
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
                    | BOLD_E_E
        '''

    def p_italic(self, p):
        '''
        italic    : ITALIC_S line_content italic_end
        '''
        p[0] = '<i>%s</i>' % p[2]
        
    def p_italic_end(self, p):
        '''
        italic_end    : ITALIC_E
                        | ITALIC_E_E
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
                        |    UNDERLINE_E_E
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
