

from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
import context
from context import Context
from bases.strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

import libs.bytes as lbytes

from cases.utils import *
from tests.utils import *

import libs.bytes as lbytes


class TestLibs(TestCase):


    def test_bytes_lib_xor(self):
        ''' '''
        r1 = lbytes.bit_xor(0, BytesVal(bytearray2(b'\xf0\xf0')), BytesVal(bytearray2(b'\xff\x00')))
        self.assertEqual(b'\x0f\xf0', bytes(r1.val))
        
        r2 = lbytes.bit_xor(0, BytesVal(bytearray2(b'\x12\x09\xdf')), BytesVal(bytearray2(b'\xff\x00')))
        self.assertEqual(b'\x12\xf6\xdf', bytes(r2.val))

    def test_bytes_lib_or(self):
        ''' '''
        r1 = lbytes.bit_or(0, BytesVal(bytearray2(b'\xf0\xf0')), BytesVal(bytearray2(b'\xff\x00')))
        self.assertEqual(b'\xff\xf0', bytes(r1.val))
        
        r2 = lbytes.bit_or(0, BytesVal(bytearray2(b'\x12\x09\xdf')), BytesVal(bytearray2(b'\xff\x00')))
        self.assertEqual(b'\x12\xff\xdf', bytes(r2.val))

    def test_bytes_lib_and(self):
        ''' '''
        r1 = lbytes.bit_and(0, BytesVal(bytearray2(b'\xf0\xf0')), BytesVal(bytearray2(b'\xff\x00')))
        self.assertEqual(b'\xf0\x00', bytes(r1.val))
        
        r2 = lbytes.bit_and(0, BytesVal(bytearray2(b'\xa1\xe2')), BytesVal(bytearray2(b'\x00\xf0\x0f')))
        self.assertEqual(b'\x00\xa0\x02', bytes(r2.val))


if __name__ == '__main__':
    main()
