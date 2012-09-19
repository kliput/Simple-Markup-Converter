#!/usr/bin/env python3

# -*- coding: utf-8 -*-

from main import SimpleMarkupConverter, Exit
import re
import unittest

class SimpleMarkupConverterTests(unittest.TestCase):
    '''
    Testy jednostkowe dla SimpleMarkupConverter.
    '''

    def setUp(self):
        pass

    # === Txt2Tags ===

    # sprawdzenie prostego parsowania akapitów txt2tags na xml 
    def test_txt2tags_plain_par_to_html(self):
        f = open('tests/t2t_plain_3par.txt')
        text = f.read()
        f.close()
        smc = SimpleMarkupConverter(input=text,
                                    input_t='txt2tags', output_t='html')
        # powodzenie w działaniu
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertNotEqual(output, '')
        self.assertEqual(output.count('<p>'), output.count('</p>'))
        self.assertEqual(output.count('<p>'), 3)

    def test_txt2tags_empty_to_html(self):
        f = open('tests/empty.txt')
        text = f.read()
        f.close()
        smc = SimpleMarkupConverter(input=text,
                                    input_t='txt2tags', output_t='html')
        # powodzenie w działaniu
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertEqual(output, '')
    
    def test_t2t_bold1(self):
        smc = SimpleMarkupConverter(input='lorem **ipsum sit** dolor amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        # poprawne wyjście - konwersja tagów jeden raz
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*ipsum\s*sit\s*\<\/b\>',
                                           smc.get_output())))

    def test_t2t_bold2(self):
        smc = SimpleMarkupConverter(input='lorem ** ipsum sit** dolor amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        # brak konwersji tagów
        self.assertTrue(smc.get_output().count('<b>') == smc.get_output().count('</b>') == 0)

    def test_t2t_bold3(self):
        smc = SimpleMarkupConverter(input='lorem **ipsum sit ** dolor** amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        # jeden zakres bold ipsum-dolor
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*ipsum\s*sit\s*\*\*\s*dolor\s*\<\/b\>',
                                           smc.get_output())))

    def test_t2t_bold4(self):
        smc = SimpleMarkupConverter(input='**lorem ipsum** **sit dolor** ** amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        # 2 zakresy bold
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*lorem\s*ipsum\s*\<\/b\>',
                                           smc.get_output())))
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*sit\s*dolor\s*\<\/b\>',
                                           smc.get_output())))

    # formatowanie zagnieżdżone (bold<-italic)
    def test_t2t_formats1(self):
        smc = SimpleMarkupConverter(input='**lorem //ipsum sit// dolor** amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        rx = re.compile(r'''
        \<b\> \s* lorem \s* \<i\> \s* ipsum \s* sit \s* \<\/i\> \s* dolor \s* \<\/b\> \s* amet 
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))

    # bold, italic, underline "przemieszane"
    def test_t2t_formats2(self):
        smc = SimpleMarkupConverter(input='**lorem __//ipsum// sit dolor__** amet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        rx = re.compile(r'''
        \<b\>\s*lorem \s*\<u\>\s*\<i\>\s*ipsum\s*\<\/i\> \s*sit \s*dolor\s*\<\/\u\>\s*\<\/b\>\s* amet
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    
    # nagłówek pojedynczy
    def test_t2t_head1(self):
        smc = SimpleMarkupConverter(input='lorem ipsum\n\n =sit dolor =\namet',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        rx = re.compile(r'''
        \<h1\>\s*sit\s*dolor\s*\<\/h1\>
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    def test_t2t_head2(self):
        smc = SimpleMarkupConverter(input='= lorem ipsum =\n\n\n\t   ==== sit dolor ====',
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        r1 = re.compile(r'''
        \<h1\>\s*lorem\s+ipsum\s*\<\/h1\>
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                r1.findall(smc.get_output())
                                ))
        r4 = re.compile(r'''
        \<h4\>\s*sit\s+dolor\s*\<\/h4\>
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                r4.findall(smc.get_output())
                                ))
    def test_t2t_list(self):
        text = '''
        Lista wypunktowana:
        - jeden
        - dwa
        - trzy
        piecdzciesiat
        
        Akapit ostatni
        '''
        smc = SimpleMarkupConverter(input=text,
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        
        r_li = re.compile(r'''
        \<li\>.+?\<\/li\>
        ''', re.DOTALL | re.VERBOSE)
                
        r_p = re.compile(r'''
        \<p\>\s*Lista\s+wypunktowana:\s*\<\/p\>
        ''', re.VERBOSE)
        
        self.assertEqual(3, len(r_li.findall(smc.get_output())))
        self.assertEqual(1, len(r_p.findall(smc.get_output())))

    def test_t2t_enum(self):
        text = '''
        Lista numerowana:
        + jeden
        + dwa
        + trzy
        '''
        smc = SimpleMarkupConverter(input=text,
                                    input_t='txt2tags', output_t='html')
        smc.parse()
        
        r_li = re.compile(r'''
        \<li\>.+?\<\/li\>
        ''', re.DOTALL | re.VERBOSE)
                
        r_p = re.compile(r'''
        \<p\>\s*Lista\s+numerowana:\s*\<\/p\>
        ''', re.VERBOSE)
        
        self.assertEqual(3, len(r_li.findall(smc.get_output())))
        self.assertEqual(1, len(r_p.findall(smc.get_output())))
        
    def test_t2t_list_nested(self):
        f = open('tests/t2t_list.txt')
        text = f.read()
        f.close()
        smc = SimpleMarkupConverter(input=text,
                                    input_t='txt2tags', output_t='html')
        
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        
        r_list = re.compile(r'''
\<ul\>\s*\<li\>\s*lorem\s*
\<\/li\>\s*
\<ul\>\s*\<li\>\s*ipsum\s*
\<\/li\>\s*
\<li\>\s*sit\s*
\<\/li\>\s*\<\/ul\>\s*
\<li\>\s*dolor\s*
\<\/li\>\s*
\<li\>\s*amet\s*
\<\/li\>\s*
\<ul\>\s*\<li\>\s*lorem\s*
\<\/li\>\s*\<\/ul\>\s*
\<li\>\s*ipsum\s*\<\/li\>\s*\<\/ul\>
        ''', re.VERBOSE)

        self.assertEqual(1, len(r_list.findall(smc.get_output())))

    # TODO mieszane t2t ol/ul
    
    # TODO test dla t2t->t2t

    # === Textile ===
    
    def test_textile_formats1(self):
        smc = SimpleMarkupConverter(input='*lorem _ipsum sit_ dolor* +amet+',
                                    input_t='textile', output_t='html')
        self.assertEqual(smc.parse(), Exit.SUCCESS)

        print(smc.get_output())
        
        rx = re.compile(r'''
        \<b\> \s* lorem \s* 
        \<i\> \s* ipsum \s* sit \s* \<\/i\>
        \s* dolor \s* \<\/b\>
        \s* \<u\>amet\<\/u\> 
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    
    # formatowanie zagnieżdżone (bold<-italic)
    def test_textile_par1(self):
        text = '''
Pierwszy akapit

Drugi
wieloliniowy
akapit



Po przerwie
'''
        smc = SimpleMarkupConverter(input=text,
                                    input_t='textile', output_t='html')
        self.assertEqual(smc.parse(), Exit.SUCCESS)

        print(smc.get_output())
        
        rx = re.compile(r'''
\<p\>\s*Pierwszy\s+akapit\s*\<\/p\>\s*
\<p\>\s*Drugi\s*\<br\/\>\s*wieloliniowy\s*\<br\/\>\s*akapit\s*\<\/p\>\s*
\<p\>\s*Po\s+przerwie\s*\<\/p\>
        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    
    def test_textile_headers(self):
        text = '''
h1. Lorem
ipsum

Some multiline
paragraph

h2. Sit dolor

 h3. Amet
        '''
    
        smc = SimpleMarkupConverter(input=text,
                                    input_t='textile', output_t='html')
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        
        print(smc.get_output())
        
        r1 = re.compile(r'''
        \<h1\>\s*Lorem\s+ipsum\s*\<\/h1\>
        ''', re.VERBOSE)
        
        r2 = re.compile(r'''
        \<h2\>\s*Sit\s+dolor\s*\<\/h2\>
        ''', re.VERBOSE)
        
        # spacja przed h3. wyłącza wykrywanie nagłówka
        r3 = re.compile(r'''
        h3\.\s+Amet
        ''', re.VERBOSE)
        
        self.assertEqual(1, len(
                                r1.findall(smc.get_output())
                                ))
        self.assertEqual(1, len(
                                r2.findall(smc.get_output())
                                ))
                                
        self.assertEqual(1, len(
                                r3.findall(smc.get_output())
                                ))

    # lista wypunktowana zagnieżdżona
    def test_textile_lists1(self):
        text = '''
* Lorem
* Ipsum sit
** Dolor amet
** Lorem ipsum
* Sit dolor
'''
        smc = SimpleMarkupConverter(input=text,
                                    input_t='textile', output_t='html')
        self.assertEqual(smc.parse(), Exit.SUCCESS)

        print(smc.get_output())
        
        rx = re.compile(r'''
\<ul\>\s*\<li\>\s*Lorem\s*\<\/li\>\s*
\<li\>\s*Ipsum\s+sit\s*\<\/li\>\s*
\<ul\>\s*\<li\>\s*Dolor\s+amet\s*\<\/li\>\s*
\<li\>\s*Lorem\s+ipsum\s*\<\/li\>\s*\<\/ul\>\s*
\<li\>\s*Sit\s+dolor\s*\<\/li\>\s*\<\/ul\>

        ''', re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))

if __name__ == '__main__':
    unittest.main()
