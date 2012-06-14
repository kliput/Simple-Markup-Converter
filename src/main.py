#!/usr/bin/env python3

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

import sys
import ply.lex as lex

from txt2tags import Txt2Tags

if __name__ == '__main__':
        try:
            f = open(sys.argv[1], "r")
        except:
            print("File open error")
            exit(1)
        
        text = f.read()
        
        input_parser = Txt2Tags()
        
        try:
            output = input_parser.run(text)
        except lex.LexError as e:
            print("Parsing error:", e)
        else:
            print(output);
