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

    # TODO test zagnieżdżania bold w bold (ma być fail)
    # TODO test zagnieżdżania różnych typów tagów
    # TODO test mieszanego zagnieżdżania (BIBbib)

if __name__ == '__main__':
    unittest.main()
