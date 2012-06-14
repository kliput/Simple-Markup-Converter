import re

import translator

class ExampleTranslator(Translator):

    tokens = (
        'TYPE',
        'ID',
        'NAME',
        'VALUE',
        'EQ',
        'COMMA',
    )

    states = (
        ('idstat', 'inclusive'),
        ('namestat', 'inclusive'),
        ('valuestat', 'inclusive'),
    )
    
    # literaly, ktore nie zmienia stanu
    literals = ['@', '{', ',', '}']
    
    # pomocniczo: pola obowiazkowe dla poszczegolnych typow
    req_fields = {'book': 'publisher', 'article': 'journal', 'inproceedings': 'booktitle'}
    
    # aktualnie przetwarzany typ
    current_type = None
    # aktualnie przetwarzany klucz
    current_name = None
    
    # aktualnie wykorzystane name-y w publikacji
    name_list = []
    
    # dotychczas uzyte id
    id_list = []
    
    # typ publikacji -> pierwszy token
    def t_INITIAL_TYPE(self, t):
        '''\w+'''
        t.lexer.begin('idstat')
        return t

    # id
    def t_idstat_ID(self, t):
        '''\w+(?=,)'''
        t.lexer.begin('namestat')
        return t
    
    # nazwa pola
    def t_namestat_NAME(self, t):
        '''\w+'''
#        t.value = t.value.lower()    # wielkosc znakow dowolna - ZANIECHANE, robione pozniej
        return t
    
    # literal = zmieniajacy stan (name = value)
    def t_namestat_EQ(self, t):
        '''='''
        t.lexer.begin('valuestat')
        return t
    
    # wartosc pola, robi dodatkowe potrzebne przeksztalcenia
    def t_valuestat_VALUE(self, t):
        '''(\w+)|(\".*?\")'''
        
        # przeksztalcenie cudzyslowiow
        if t.value[0] == t.value[-1] == '"':
            quot = True
            work = t.value[1:-1]
        else:
            quot = False
            work = t.value
        
        # jesli to author - wstawia dodatkowe + po literze imienia
        if self.current_name == 'author':
            work = re.sub(r'([A-Z])\. (\w)', r'\1.+\2', work)
        
        if quot == True:
            t.value = "'" + work + "'"
        else:
            t.value = work
        
        return t

    # literal zmieniajacy stan
    def t_valuestat_COMMA(self, t):
        ''','''
        t.lexer.begin('namestat')
        return t
    
    def t_ANY_error(self, t):
        print("token error: ", t)

    def t_ANY_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
    
    t_ANY_ignore = ' \t'
    
    
    # glowne
    def p_publications(self, p):
        '''
        publications    : publications publication
        '''
        p[0] = '%s\n%s' % (p[1], p[2])
        if p[2] != None:
            print(p[2])
    
    def p_publications_empty(self, p):
        '''
        publications    :
        '''
    
    # bledna publikacja
    def p_publications_error(self, p):
        '''
        publications    : publications error
        '''
        print('error: wrong publication definition')
        p[0] = ''
    
    def p_publication_error_content(self, p):
        '''
        publication        : '@' type '{' id ',' error '}'
        '''
        # wyswietlenie komunikatu z ostatnia nazwa id
        print("error: wrong fields in publication: '%s', skipping" % (self.id_list[-1]))
        self.name_list = []
        p.lexer.begin('INITIAL')

    def p_publication_error_type(self, p):
        '''
        publication        : '@' error '{' id ',' fields '}'
        '''
        print("error: wrong publication type: '%s', skipping" % (p.value))
        self.name_list = []
        raise SyntaxError    # przerzucenie do gory
    
    # poprawna publikacja
    def p_publication(self, p):
        '''
        publication        : '@' type '{' id ',' fields '}'
        '''
        
        # sprawdzenie, czy wystepuja pola obowiazkowe (dla danego typu)
        for nam in ['author', 'title', 'year', self.req_fields[self.current_type]]:
            if nam not in self.name_list:
                print("error: missing field '%s' in '%s'" % (nam, p[4]))
                p.lexer.begin('INITIAL')
                raise SyntaxError
            else:
                self.name_list.remove(nam)    # usuniecie - pozniej sprawdzenie, czy cos nie zostalo
        
        if len(self.name_list) != 0:
            raise SyntaxError
        
        p.lexer.begin('INITIAL')
        p[0] = "%s'%s': {\n%s}" % (p[2], p[4], p[6])
    
    # typ publikacji
    def p_type(self, p):
        '''
        type    : TYPE
        '''
        
        self.current_type = p[1].lower()
        
        if self.current_type not in ['book', 'article', 'inproceedings']:
            print("error: unknown type '%s'" % p[1])
            raise SyntaxError
        
        # zachowanie oryginalnej pisowni
        p[0] = '%s{' % (p[1])
    
    # sprawdzenie, czy identyfikator sie nie powtorzyl
    def p_id(self, p):
        '''
        id    : ID
        '''
        if p[1].lower() not in self.id_list:
            self.id_list.append(p[1].lower())
            p[0] = p[1]
        else:
            print("error: duplicate id '%s'" % (p[1]))
            raise SyntaxError
    
    # pola oddzielone przecinkiem
    def p_fields_multi(self, p):
        '''
        fields    : fields COMMA field
        '''
        p[0] = '%s\t%s,\n' % (p[1], p[3])
    
    # osstatnie pole
    def p_fields_last(self, p):
        '''
        fields    : field
        '''
        p[0] = '\t%s\n' % (p[1],)
    
    # pojedyncze pole
    def p_field(self, p):
        '''
        field    : name EQ value
        '''
        p[0] = '%s\t: %s' % (p[1], p[3])

    # pojedyncze pole - bledna nazwa
    def p_field_error_name(self, p):
        '''
        field    : error EQ value
        '''
        print('error: bad field name')
        raise SyntaxError    # error do gory
#        p[0] = '%s\t: %s' % (p[1], p[3])

    def p_name(self, p):
        '''
        name    : NAME
        '''
        if (p[1].lower() in ['author', 'title', 'year']) or (self.current_type == 'book' and p[1] == 'publisher') or (self.current_type == 'article' and p[1] == 'journal') or (self.current_type == 'inproceedings' and p[1] == 'booktitle'):
            p[0] = p[1]
            self.current_name = p[0].lower()
            # czy powtorzenie pola name?
            # (nadmiarowe, bo pozniej jest sprawdzanie, ale dla wczesniejszego wykrycia)
            if self.current_name in self.name_list:
                raise SyntaxError
            # dodanie pola name na tymczasowa liste
            self.name_list.append(self.current_name)
        else:
            # calkiem niepoprawne pole, albo niepasujace do typu
            raise SyntaxError

    # wartosc pola
    def p_value(self, p):
        '''
        value    : VALUE
        '''
        p[0] = p[1]
    
    def p_error(self, p):
        print("syntax error in line %d: ...%s..." % (p.lineno, p.value))
