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
        self.seq = range(10)

    # sprawdzenie prostego parsowania akapitów txt2tags na xml 
    def test_txt2tags_plain_par_to_xml(self):
        smc = SimpleMarkupConverter(file='tests/t2t_plain_3par.txt')
        # powodzenie w działaniu
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertNotEqual(output, '')
        self.assertEqual(output.count('<p>'), output.count('</p>'))
        self.assertEqual(output.count('<p>'), 3)

    def test_txt2tags_empty_to_xml(self):
        smc = SimpleMarkupConverter(file='tests/empty.txt')
        # powodzenie w działaniu
        self.assertEqual(smc.parse(), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertEqual(output, '')
    
    def test_t2t_bold1(self):
        smc = SimpleMarkupConverter(input='lorem **ipsum sit** dolor amet')
        smc.parse()
        # poprawne wyjście - konwersja tagów jeden raz
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*ipsum\s*sit\s*\<\/b\>', 
                                           smc.get_output())))

    def test_t2t_bold2(self):
        smc = SimpleMarkupConverter(input='lorem ** ipsum sit** dolor amet')
        smc.parse()
        # brak konwersji tagów
        self.assertTrue(smc.get_output().count('<b>') == smc.get_output().count('</b>') == 0)

    def test_t2t_bold3(self):
        smc = SimpleMarkupConverter(input='lorem **ipsum sit ** dolor** amet')
        smc.parse()
        # jeden zakres bold ipsum-dolor
        self.assertEqual(1, len(
                                re.findall(r'\<b\>\s*ipsum\s*sit\s*\*\*\s*dolor\s*\<\/b\>', 
                                           smc.get_output())))

    def test_t2t_bold4(self):
        smc = SimpleMarkupConverter(input='**lorem ipsum** **sit dolor** ** amet')
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
        smc = SimpleMarkupConverter(input='**lorem //ipsum sit// dolor** amet')
        smc.parse()
        rx = re.compile(r'''
        \<b\> \s* lorem \s* \<i\> \s* ipsum \s* sit \s* \<\/i\> \s* dolor \s* \<\/b\> \s* amet 
        ''',  re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))

    # bold, italic, underline "przemieszane"
    def test_t2t_formats2(self):
        smc = SimpleMarkupConverter(input='**lorem __//ipsum// sit dolor__** amet')
        smc.parse()
        rx = re.compile(r'''
        \<b\>\s*lorem \s*\<u\>\s*\<i\>\s*ipsum\s*\<\/i\> \s*sit \s*dolor\s*\<\/\u\>\s*\<\/b\>\s* amet
        ''',  re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    
    # nagłówek pojedynczy
    def test_t2t_head1(self):
        smc = SimpleMarkupConverter(input='lorem ipsum\n\n =sit dolor =\namet')
        smc.parse()
        rx = re.compile(r'''
        \<h1\>\s*sit\s*dolor\s*\<\/h1\>
        ''',  re.VERBOSE)
        self.assertEqual(1, len(
                                rx.findall(smc.get_output())
                                ))
    

if __name__ == '__main__':
    unittest.main()
