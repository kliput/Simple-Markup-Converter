#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright (C) 2012 Jakub Liput, Mirosław Sajdak
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

from translator.txt2tags import Txt2TagsInput, Txt2TagsOutput
from translator.dummy import PassTranslator
from ply import lex, yacc
import sys

# stałe kierunku translacji
IN = "input"
OUT = "output"

# przechowuje odwzorowanie kodu_<input/output> -> klasa translatora
translator_map = {
#                  "txt2tags":
#                  {IN: Txt2TagsInput, OUT: Txt2TagsInput },
                  "dummy":
                  {IN: PassTranslator, OUT: PassTranslator }
                }

if __name__ == '__main__':
        # TODO: parametry wywołania - parsing:
        # ./smc [-o output_file] --iformat=code_input --oformat=code_output input_file
        # -o plik wyjściowy (opcjonalne, może wypisać na stdout)
        # -iformat kod_formatu_wejściowego
        # -oformat kod_formaty_wyjściowego
        # kody: txt2tags, textile, dokuwiki, html (tylko wyjściowe)
        
        # otworzenie pliku z parametru
        try:
            f = open(sys.argv[1], "r")
        except Exception as e:
            print("File open error: %s" % str(e))
            exit(1)
        
        # odczyt pliku
        try:
            text = f.read()
        except Exception as e:
            print("File read error: %s" % str(e))
            exit(1)
        
        # TODO: wczytanie z linii komend
        # wybór odpowiednich translatorów wejściowych/wyjściowych
        file_format = {}
        file_format[IN] = "dummy"
        file_format[OUT] = "dummy"
        
        translator = {}
        
        # TODO: można obsłużyć gdy jest translator, ale w nie w tą stronę
        try:
            # wyszukanie w mapie odpowiednich translatorów we/wy i ich konstrukcja
            for direction in [IN, OUT]:
                translator_type = translator_map[file_format[direction]][direction]
                translator[direction] = translator_type()
        except KeyError:
            print("Wrong %s format specified: %s" % (direction, file_format[direction]))
            exit(2)
        except SyntaxError as e:
            # błąd w konstrukcji translatora
            print("Construction of %s parser %s failed: %s" % (direction, translator_type.__name__, e))
            exit(4)
        except yacc.LALRError as e:
            print("Construction of %s parser %s failed: %s" % (direction, translator_type.__name__, e))
            exit(4)
            
        try:
            # wywoływanie kolejnych translatorów
            for direction in [IN, OUT]:
                text = translator[direction].run(text)
            # TODO: możliwy tryb wyjścia do pliku
            print(text)
            exit(0)
        except lex.LexError as e:
            print("Translation %s lexer error: %s" % (direction, e))
        except Exception as e:
            print("Error: %s" % str(e))
        
        # zakończono niepowodzeniem
        exit(3)
        
        
