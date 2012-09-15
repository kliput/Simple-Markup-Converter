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
        
    
    tokens = (
        'PAR_S',
        'PAR_E',
        'BOLD_S',
        'BOLD_E',
        'ITALIC_S',
        'ITALIC_E',
        'UNDERLINE_S',
        'UNDERLINE_E',
        'WORD',
    )
    
    states = (
        ('p', 'inclusive'), # <p>...
        ('b', 'inclusive'), # <b>...
        ('i', 'inclusive'), # <i>...
        ('u', 'inclusive'), # <u>...
    )
    
    t_ANY_ignore = ' \t\n'
    
    # === TOKENY ===
    
    # ------ tagi ------
    
    # <p>
    
    def t_INITIAL_PAR_S(self, t):
        r'\<p\>'
        t.lexer.push_state('p')
        self.log.debug(r'<p>');
        return t

    def t_p_PAR_E(self, t):
        r'\<\/p\>'
        t.lexer.pop_state()
        self.log.debug(r'</p>');
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

    # ------ słowa ------
    
    # ten token powinien być wykrywany w stanach dla każdego taga
    # słowo, po którym następuje koniec jakiegoś taga
    def t_p_b_i_u_WORD(self, t):
        r'[^\s]+?(?=\s*\<\/)'
        self.log.debug('WORD tag end token: ' + t.value)
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
        '''
        self.log.debug('block: par (%s)' % (p[1]))
        p[0] = '%s' % (p[1])
        
    def p_paragraph(self, p):
        '''
        paragraph    : PAR_S content PAR_E
        '''
        self.log.debug('par <p> content (%s) <\/p>' % (p[2]))
        p[0] = '%s\n\n' % (p[2])

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
        self.log.debug('cont: element (%s)' % (p[1]))
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
        '''
        self.log.debug(r'plain multi (%s) word (%s)' % (p[1], p[2]))
        p[0] = p[1] + ' ' + p[2]
        
    def p_plain_single(self, p):
        '''
        plain   : WORD
        '''
        self.log.debug(r'plain single word (%s)' % (p[1]))
        p[0] = p[1]

    # tagi formatowania

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
    
    