#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import unittest
from main import SimpleMarkupConverter, Exit

class SimpleMarkupConverterTests(unittest.TestCase):
    '''
    Testy jednostkowe dla SimpleMarkupConverter.
    '''

    def setUp(self):
        self.seq = range(10)

    # sprawdzenie prostego parsowania akapitów txt2tags na xml 
    def test_txt2tags_plain_par_to_xml(self):
        smc = SimpleMarkupConverter(store_output=True)
        # powodzenie w działaniu
        self.assertEqual(smc.start('tests/t2t_plain_3par.txt'), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertNotEqual(output, '')
        self.assertEqual(output.count('<p>'), output.count('</p>'))
        self.assertEqual(output.count('<p>'), 3)

    def test_txt2tags_empty_to_xml(self):
        smc = SimpleMarkupConverter(store_output=True)
        # powodzenie w działaniu
        self.assertEqual(smc.start('tests/empty.txt'), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertEqual(output, '')
    
    def test_txt2tags_bold(self):
        smc = SimpleMarkupConverter(store_output=True)
        smc.start('tests/bold.t2t')
        print('===== txt2tags bold test =====')
        print(smc.output)
        print('=====')

if __name__ == '__main__':
    unittest.main()
