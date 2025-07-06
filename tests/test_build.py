
'''
Test build.py functions
'''

import pathlib
from unittest import TestCase, main

from build import *
from main import *
from run import *


class tArgs:
    ''' testing CI options '''
    def __init__(self, arg=None, code=None):
        self.src = arg
        self.codeline = code


class TestBuild(TestCase):
    
    def test_src_file(self):
        ''' '''
        args = tArgs('tests%stbuild_src.et' % pathlib.os.sep)
        src = getSource(args)
        self.assertEqual('a = 10', src)
    
    def test_src_codeline(self):
        ''' '''
        srcArg = 'b = 20'
        args = tArgs(srcArg, code=True)
        src = getSource(args)
        self.assertEqual('b = 20', src)


if __name__ == '__main__':
    main()
