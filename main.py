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

from ply import lex
from translator.dummy import PassTranslator
from translator.txt2tags import Txt2TagsToHTML
from translator.html_to_t2t import HtmlToTxt2Tags
from translator.textile_to_html import TextileToHTML
import argparse
import logging

class Exit(object):
    SUCCESS = 0
    FILE_ERROR = 1
    WRONG_CMD = 2
    TRANSLATION_ERROR = 3
    PARSER_CONSTRUCTION_FAIL = 4
    NO_INPUT = 5
    
    
class SimpleMarkupConverter(object):
    
    # przechowywany tekst wyjściowy po parse()
    output = ''

    # flaga, czy wykonano już parsowanie
    is_parsed = False

    # stałe kierunku translacji
    IN = "input"
    OUT = "output"
    
    # przechowuje odwzorowanie kodu_<input/output> -> klasa translatora
    translator_map = {
                      "pass":
                      {IN: PassTranslator, OUT: PassTranslator },
                      "html":
                      {OUT: PassTranslator},
                      "txt2tags":
                      {IN: Txt2TagsToHTML, OUT: HtmlToTxt2Tags},
                      "textile":
                      {IN: TextileToHTML}
                    }

    def __init__(self, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)
        
        log_level = logging.INFO
        
        if 'verbose' in kwargs:
            if kwargs['verbose'] == True:
                log_level = logging.DEBUG
                        
        logging.basicConfig(format='%(levelname)s[%(name)s]: %(message)s', level=log_level)

        if 'input' in kwargs:
            self.input = kwargs['input']
        else:
            self.log.error('No input specified.')
            return(Exit.NO_INPUT)


        file_format = {}
        try:
            file_format[self.IN] = kwargs['input_t']
        except KeyError:
            self.log.error('No input translator specified')
            return Exit.WRONG_CMD
        try:
            file_format[self.OUT] = kwargs['output_t']
        except KeyError:
            self.log.error('No output translator specified')
            return Exit.WRONG_CMD
        
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
        if not self.is_parsed:
            self.log.warn('get_output: parse() was not invoked!')
        return self.output
    
    def parse(self):
        
        text = self.input
        
        try:
            # wywoływanie kolejnych translatorów
            for direction in [self.IN, self.OUT]:
                text = self.translator[direction].run(text)
            
            if self.input == None:
                raise Exception("None parser output")
            
            self.output = text
            
            self.is_parsed = True
            
            return Exit.SUCCESS
        except lex.LexError as e:
            print("Translation %s lexer error: %s" % (direction, e))
        except Exception as e:
            print("Error: %s" % (e))
        
        # zakończono niepowodzeniem
        return Exit.TRANSLATION_ERROR

# program główny
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('input_type', help='input markup language: ')
    ap.add_argument('output_type', help='output markup language: txt2tags')
    ap.add_argument('-o', '--output_file', help='output file path: html')
    ap.add_argument('input_file', help='input file')
    ap.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug messages')    
    res = ap.parse_args()
    
    # otworzenie pliku z parametru
    try:
        f = open(res.input_file, "r")
    except Exception as e:
        print("File open error: %s" % str(e))
        exit(Exit.FILE_ERROR)
    
    # odczyt pliku
    try:
        text_input = f.read()
    except Exception as e:
        print("File read error: %s" % str(e))
        exit(Exit.FILE_ERROR)
    
    # konstrukcja z plikiem wejściowycm
    smc = SimpleMarkupConverter(
                                input=text_input,
                                input_t=res.input_type,
                                output_t=res.output_type,
                                verbose=res.verbose
                                )
    exit_code = smc.parse()
    
    if exit_code == Exit.SUCCESS:
        if res.output_file:
            f = open(res.output_file, 'w')
            f.write(smc.get_output())
            f.close()
        else:
            print(smc.get_output())
    else:
        print('An error occured while parsing.')
        
    exit(exit_code)