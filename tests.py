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
        self.assertEqual(smc.start('tests/t2t_plain.txt'), Exit.SUCCESS)
        # sprawdzenie wyjścia
        output = smc.get_output()
        self.assertNotEqual(output, '')
        self.assertEqual(output.count('<p>'), output.count('</p>'))
        self.assertEqual(output.count('<p>'), 3)

if __name__ == '__main__':
    unittest.main()
