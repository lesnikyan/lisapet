'''
Test of error handling of parser, interpreter and executor.

'''

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from cases.utils import *
from tree import *
from eval import *



class TestErr(TestCase):


# error handling

    def runErr(self, code):
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        return ex
        # self.assertFalse(isinstance(ex, Expression))

    def doErr(self, code, ctx):
        expr = self.runErr(code)
        expr.do(ctx)

    def tctx(self):
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        return rCtx, ctx

    def _test_err_exec(self):
        ''' '''
        data = [
            'x = 2 + m',
            # '""++123',
            # 'func 123\n',
            # 'if 1:\n',
            # '~~::',
            # '1....2',
            # '())',
            # 'if \nelse \nif \nelse func()',
        ]
        for code in data:
            # try:
            # except LangError:
            print('TEST.code: ', code)
            with self.assertRaises(InterpretErr) as cont:
                rCtx, ctx =self.tctx()
                self.doErr(code, ctx)
                print('>>TT err:', cont.exception)

    def test_err_interpret(self):
        ''' '''
        data = [
            '--123',
            '""++123',
            'func 123\n',
            'if 1:\n',
            '~~::',
            '1....2',
            '())',
            # 'if \nelse \nif \nelse func()',
        ]
        for code in data:
            # try:
            # except LangError:
            print('TEST.code: ', code)
            with self.assertRaises(InterpretErr) as cont:
                self.runErr(code)
                print('>>TT err:', cont.exception)

    def test_err_parse(self):
        ''' '''
        data = [
            "'",
            '"123',
            '"\\"',
            '"\\g"',
            '"\\0"',
            # 'x> >>>>',
        ]
        for code in data:
            # try:
            # except LangError:
            print('TEST.code: ', code)
            with self.assertRaises(ParseErr) as cont:
                self.runErr(code)
                print('>>TT err:', cont.exception)


if __name__ == '__main__':
    main()
