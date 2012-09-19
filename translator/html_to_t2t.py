# -*- coding: utf-8 -*-

from .translator import Translator
import re


class HtmlToTxt2Tags(Translator):
    '''
    Translator tHTML (języka wewnętrznego) -> Txt2Tags
    '''
        
    def __init__(self):
        super().__init__()
        self.log.debug('%s constructor' % self.__class__.__name__)

    # o ile ma zawiększyć następnym razem wcięcie listy
    indent_next = 0
    # aktualny poziom wcięcia listy
    indent_lvl = -1
    # czy to koniec glównego bloku listy
    list_final = False
    
    # Jeśli jest to pierwsze wejście do <ul>, zwiększa natychmiast,
    # jeśli nie - będzie oczekiwać na wywołanie change_indent
    def delay_inc_indent(self):
        if self.indent_lvl == -1:
            self.log.debug('first inc indent')
            self.indent_lvl += 1
        else:
            self.log.debug('next inc indent')
            self.indent_next = 1
        
    # Jeśli jest to ostatnie wyjście z </ul>, zmniejsza natychmiast,
    # jeśli nie - będzie oczekiwać na wywołanie change_indent
    def delay_dec_indent(self):
        if self.indent_lvl == 0:
            self.log.debug('last dec indent')
            self.indent_lvl -= 1
            self.list_final = True
        else:
            self.log.debug('next dec indent')
            self.indent_next = -1
        
    
    # zmiana aktualnego poziomu wcięcia
    def change_indent(self):
        self.log.debug('change_indent: %s -> %s' % (self.indent_lvl, self.indent_lvl+self.indent_next))
        self.indent_lvl += self.indent_next
        self.indent_next = 0

    tokens = (
        'PAR_S',
        'PAR_E',
        'BOLD_S',
        'BOLD_E',
        'ITALIC_S',
        'ITALIC_E',
        'UNDERLINE_S',
        'UNDERLINE_E',
        'UL_S',
        'UL_E',
        'OL_S',
        'OL_E',
        'LI_S',
        'LI_E',
        'H_S',
        'H_E',
        'WORD',
        'BR',
    )
    
    states = (
        ('p', 'inclusive'), # <p>...
        # formatowanie
        ('b', 'inclusive'), # <b>...
        ('i', 'inclusive'), # <i>...
        ('u', 'inclusive'), # <u>...
        # listy
        ('ul', 'inclusive'), # <ul>...
        ('ol', 'inclusive'), # <ol>...
        ('li', 'inclusive'), # <li>...
        # nagłówki
        ('h1', 'inclusive'),
        ('h2', 'inclusive'),
        ('h3', 'inclusive'),
        ('h4', 'inclusive'),
        ('h5', 'inclusive'),
        
    )
    
    t_ANY_ignore = ' \t\n'
    
    # === TOKENY ===
    
    # ------ tagi ------
    
    # <br/>
    def t_ANY_BR(self, t):
        r'\<br\/\>'
        t.value = r'\\'
        return t
    
    # <p>
    
    def t_INITIAL_PAR_S(self, t):
        r'\<p\>'
        t.lexer.push_state('p')
        self.log.debug(r'<p>')
        return t

    def t_p_PAR_E(self, t):
        r'\<\/p\>'
        t.lexer.pop_state()
        self.log.debug(r'</p>')
        return t
    
    # --- nagłówki ---
    
    def t_INITIAL_H_S(self, t):
        r'\<h\d\>'
        lvl = re.match(r'\<h(\d)\>', t.value).group(1)
        t.lexer.push_state('h%s' % (lvl))
        t.value = '=' * int(lvl)
        self.log.debug('Heading start level: %s' % (lvl))
        return t
    
    def t_h1_H_E(self, t):
        r'\<\/h1\>'
        t.lexer.pop_state()
        t.value = '=' * 1
        self.log.debug(r'</h1>')
        return t
    
    def t_h2_H_E(self, t):
        r'\<\/h2\>'
        t.lexer.pop_state()
        t.value = '=' * 2
        self.log.debug(r'</h2>')
        return t
    
    def t_h3_H_E(self, t):
        r'\<\/h3\>'
        t.lexer.pop_state()
        t.value = '=' * 3
        self.log.debug(r'</h3>')
        return t
    
    def t_h4_H_E(self, t):
        r'\<\/h4\>'
        t.lexer.pop_state()
        t.value = '=' * 4
        self.log.debug(r'</h4>')
        return t
    
    def t_h5_H_E(self, t):
        r'\<\/h5\>'
        t.lexer.pop_state()
        t.value = '=' * 5
        self.log.debug(r'</h5>')
        return t
    
    # <b>
    
    def t_ANY_BOLD_S(self, t):
        r'\<b\>'
        t.lexer.push_state('b')
        self.log.debug(r'<b>')
        return t

    def t_b_BOLD_E(self, t):
        r'\<\/b\>'
        t.lexer.pop_state()
        self.log.debug(r'</b>')
        return t
    
    # <i>
    
    def t_ANY_ITALIC_S(self, t):
        r'\<i\>'
        t.lexer.push_state('i')
        self.log.debug(r'<i>')
        return t

    def t_i_ITALIC_E(self, t):
        r'\<\/i\>'
        t.lexer.pop_state()
        self.log.debug(r'</i>')
        return t

    # <u>
    
    def t_ANY_UNDERLINE_S(self, t):
        r'\<u\>'
        t.lexer.push_state('u')
        self.log.debug(r'<u>')
        return t

    def t_u_UNDERLINE_E(self, t):
        r'\<\/u\>'
        t.lexer.pop_state()
        self.log.debug(r'</u>')
        return t

    # --- listy ---

    # <ul>
    
    def t_INITIAL_ul_ol_UL_S(self, t):
        r'\<ul\>'
        t.lexer.push_state('ul')
        self.delay_inc_indent()
        self.log.debug(r'<ul>')
        return t

    def t_ul_UL_E(self, t):
        r'\<\/ul\>'
        t.lexer.pop_state()
        self.delay_dec_indent()
        self.log.debug(r'</ul>')
        return t

    # <ol>
    
    def t_INITIAL_ul_ol_OL_S(self, t):
        r'\<ol\>'
        t.lexer.push_state('ol')
        self.delay_inc_indent()
        self.log.debug(r'<ol>')
        return t

    def t_ol_OL_E(self, t):
        r'\<\/ol\>'
        t.lexer.pop_state()
        self.delay_dec_indent()
        self.log.debug(r'</ol>')
        return t

    # <li>
    
    def t_ul_ol_LI_S(self, t):
        r'\<li\>'
        t.lexer.push_state('li')
        self.log.debug(r'<li>')
        return t

    def t_li_LI_E(self, t):
        r'\<\/li\>'
        t.lexer.pop_state()
        self.log.debug(r'</li>')
        return t

    # ------ słowa ------
    
    # Ten token powinien być wykrywany w stanach dla każdego taga,
    # w którym może bezpośrednio leżeć słowo.
    # Słowo, po którym następuje koniec jakiegoś taga.
    def t_p_b_i_u_li_h1_h2_h3_h4_h5_WORD(self, t):
        r'[^\s]+?(?=\s*\<\/)'
        self.log.debug('WORD tag end token: ' + t.value)
        self.log.debug(str(t.lexer.lexstatestack) + ' -> ' + str(t.lexer.lexstate))
        return t
    
    # Słowo wykrywane we wszystkich trybach
    def t_WORD(self, t):
        r'[^\s]+'
        self.log.debug('WORD normal token: ' + t.value)
        return t
    
        
    # ========================    
    # PARSER    
    # ========================
    
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
    
    # akapit oddzielony od dołu
    def p_block_par(self, p):
        '''
        block    : paragraph
                    | list
                    | enum
                    | heading
        '''
        self.log.debug('block: (...) (%s)' % (p[1]))
        p[0] = '%s' % (p[1])
        
    def p_paragraph(self, p):
        '''
        paragraph    : PAR_S content PAR_E
        '''
        self.log.debug('par <p> content (%s) <\/p>' % (p[2]))
        p[0] = '%s\n\n' % (p[2])

    # sytuacja wyjątkowa, ale takie też są generowane
    def p_paragraph_empty(self, p):
        '''
        paragraph    : PAR_S PAR_E
        '''
        self.log.debug('par <p></p> (empty)')
        p[0] = '\n\n'

    def p_content(self, p):
        '''
        content   : content element
        '''
        self.log.debug('content: content %s element %s' % (p[1], p[2]))
        p[0] = p[1] + ' ' + p[2]

    def p_content_single(self, p):
        '''
        content   : element
        '''
        self.log.debug('content: (single) element (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_element(self, p):
        '''
        element    :  plain
                    | bold
                    | italic
                    | underline
        '''
        self.log.debug('element (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_plain(self, p):
        '''
        plain    : plain WORD
                    | plain BR
        '''
        self.log.debug(r'plain multi (%s) word (%s)' % (p[1], p[2]))
        p[0] = p[1] + ' ' + p[2]
        
    def p_plain_single(self, p):
        '''
        plain   : WORD
                | BR
        '''
        self.log.debug(r'plain single word (%s)' % (p[1]))
        p[0] = p[1]

    # --- obsługa tagów formatowania ---

    def p_bold(self, p):
        '''
        bold    : BOLD_S content BOLD_E
        '''
        self.log.debug(r'bold <b> content (%s) </b>' % (p[2]))
        p[0] = '**%s**' % (p[2])
    
    def p_italic(self, p):
        '''
        italic    : ITALIC_S content ITALIC_E
        '''
        self.log.debug(r'italic <i> content (%s) </i>' % (p[2]))
        p[0] = '//%s//' % (p[2])
    
    def p_underline(self, p):
        '''
        underline    : UNDERLINE_S content UNDERLINE_E
        '''
        self.log.debug(r'underline <u> content (%s) </u>' % (p[2]))
        p[0] = '__%s__' % (p[2])
    
    # ------
    
    # --- obsługa listy wypunktowanej ---
    
    def p_list(self, p):
        '''
        list    : UL_S list_content UL_E
        '''
        self.log.debug(r'list <ul> list_content (%s) </ul> lvl %s' % (p[2], self.indent_lvl))
        if self.list_final: # koniec całej listy
            p[0] = '%s\n\n\n' % (p[2])
            self.list_final = False
        else: # koniec poziomu na liście
            p[0] = '%s' % (p[2])
        
    def p_list_content(self, p):
        '''
        list_content    : list_content list_pos 
        '''
        self.log.debug(r'list_content list_content (%s) list_pos (%s)' % (p[1], p[2]))
        p[0] = '%s\n%s' % (p[1], p[2])
        
    def p_list_content_single(self, p):
        '''
        list_content    : list_pos
        '''
        self.log.debug(r'list_content list_pos (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_list_pos(self, p):
        '''
        list_pos    : LI_S content LI_E
        '''
        self.log.debug(r'list_pos <li> content (%s) </li>' % (p[2]))
        p[0] = '%s- %s' % (' '*self.indent_lvl, p[2])
        self.change_indent()
        
    # lista zagnieżdżona
    def p_list_pos_nested(self, p):
        '''
        list_pos    : list
                    | enum
        '''
        self.log.debug(r'list_pos nested (%s)' % (p[1]))
        p[0] = p[1]
        
    # --- obsługa listy numerowanej ---
    
    def p_enum(self, p):
        '''
        enum    : OL_S enum_content OL_E
        '''
        self.log.debug(r'enum <ol> enum_content (%s) </ol>' % (p[2]))
        if self.list_final: # koniec całej listy
            p[0] = '%s\n\n\n' % (p[2])
            self.list_final = False
        else: # koniec poziomu na liście
            p[0] = '%s' % (p[2])
        
    def p_enum_content(self, p):
        '''
        enum_content    : enum_content enum_pos 
        '''
        self.log.debug(r'enum_content enum_content (%s) enum_pos (%s)' % (p[1], p[2]))
        p[0] = '%s\n%s' % (p[1], p[2])
        
    def p_enum_content_single(self, p):
        '''
        enum_content    : enum_pos
        '''
        self.log.debug(r'enum_content enum_pos (%s)' % (p[1]))
        p[0] = p[1]
        
    def p_enum_pos(self, p):
        '''
        enum_pos    : LI_S content LI_E
        '''
        self.log.debug(r'enum_pos <li> content (%s) </li>' % (p[2]))
        p[0] = '%s+ %s' % (' '*self.indent_lvl, p[2])
        self.change_indent()
        
    def p_enum_pos_nested(self, p):
        '''
        enum_pos    : list
                    | enum
        '''
        self.log.debug(r'enum_pos nested (%s)' % (p[1]))
        p[0] = p[1]
        
    # --- obsługa nagłówków
    
    def p_heading(self, p):
        '''
        heading    : H_S plain H_E
        '''
        self.log.debug(r'heading <h*> plain (%s) </h*>' % (p[2]))
        p[0] = '%s %s %s\n\n' % (p[1], p[2], p[3])
