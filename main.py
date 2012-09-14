#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright (C) 2012 Jakub Liput
#
# SimpleMarkupConverter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SimpleMarkupConverter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SimpleMarkupConverter.  If not, see <http://www.gnu.org/licenses/>.

from ply import lex, yacc
from translator.dummy import PassTranslator
from translator.hello import HelloTranslator
from translator.txt2tags import Txt2TagsToXML
import logging
import sys

class Exit(object):
    SUCCESS = 0
    FILE_ERROR = 1
    WRONG_CMD = 2
    TRANSLATION_ERROR = 3
    PARSER_CONSTRUCTION_FAIL = 4
    
    
class SimpleMarkupConverter(object):

    # czy obiekt ma przechowywać tekst wyjściowy po start()?
    store_output = True
    
    # przechowywany tekst wyjściowy jeśli store_output == True
    output = ''

    # stałe kierunku translacji
    IN = "input"
    OUT = "output"
    
    # przechowuje odwzorowanie kodu_<input/output> -> klasa translatora
    translator_map = {
                      "dummy":
                      {IN: PassTranslator, OUT: PassTranslator },
                      "hello":
                      {IN: HelloTranslator},
                      "txt2tags":
                      {IN: Txt2TagsToXML},
                    }

    def __init__(self, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(format='%(levelname)s[%(name)s]: %(message)s', level=logging.DEBUG)
        
        if 'store_output' in kwargs:
            self.store_output = True
            self.log.debug('store_output turned on')

        if 'input' in kwargs and 'file' in kwargs:
            self.log.warn('"input" and "file" parameters specified, using only input')

        if 'input' in kwargs:
            self.input = kwargs['input']
        elif 'file' in kwargs:
            # TODO: parametry wywołania - parsing:
            # ./smc [-o output_file] --iformat=code_input --oformat=code_output input_file
            # -o plik wyjściowy (opcjonalne, może wypisać na stdout)
            # -iformat kod_formatu_wejściowego
            # -oformat kod_formaty_wyjściowego
            # kody: txt2tags, textile, dokuwiki, html (tylko wyjściowe)
            
            # otworzenie pliku z parametru
            try:
                f = open(kwargs['file'], "r")
            except Exception as e:
                print("File open error: %s" % str(e))
                return Exit.FILE_ERROR
            
            # odczyt pliku
            try:
                self.input = f.read()
            except Exception as e:
                print("File read error: %s" % str(e))
                return Exit.FILE_ERROR
            
        # TODO: wczytanie z linii komend
        # wybór odpowiednich translatorów wejściowych/wyjściowych
        file_format = {}
        file_format[self.IN] = "txt2tags"
        file_format[self.OUT] = "dummy"
        
        self.translator = {}
        
        # TODO: można obsłużyć gdy jest translator, ale w nie w tą stronę
        try:
            # wyszukanie w mapie odpowiednich translatorów we/wy i ich konstrukcja
            for direction in [self.IN, self.OUT]:
                translator_type = self.translator_map[file_format[direction]][direction]
                self.translator[direction] = translator_type()
        except KeyError:
            print("Wrong %s format specified: %s" % (direction, file_format[direction]))
            return Exit.WRONG_CMD
            # TODO: dawna obsługa, która jest bardziej szczegółowa
#        except (SyntaxError, yacc.LALRError) as e:
        except Exception as e:
            # błąd w konstrukcji translatora
            print("Construction of %s parser %s failed: %s" % (direction, translator_type.__name__, e))
            return Exit.PARSER_CONSTRUCTION_FAIL
                

    def get_output(self):
        return self.output
    
    def parse(self):
        
        text = self.input
        
        try:
            # wywoływanie kolejnych translatorów
            for direction in [self.IN, self.OUT]:
                text = self.translator[direction].run(text)
            
            if self.input == None:
                raise Exception("None parser output")
                
            # TODO: możliwy tryb wyjścia do pliku
#            print(text)
            
            if self.store_output:
                self.output = text
            
            return Exit.SUCCESS
        except lex.LexError as e:
            print("Translation %s lexer error: %s" % (direction, e))
        except Exception as e:
            print("Error: %s" % (e))
        
        # zakończono niepowodzeniem
        return Exit.TRANSLATION_ERROR

# program główny
if __name__ == '__main__':
    # konstrukcja z plikiem wejściowycm
    smc = SimpleMarkupConverter(store_output=True, file=(' '.join(sys.argv[1:])))
    smc.parse()
    print(smc.get_output())
