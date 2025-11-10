

from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
import context
from context import Context
from strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *
from libs.regexp import *
from cases.operwords import *



class TestRegexp(TestCase):
    ''' Test builtin regexp lib. '''



    def test_regexp_oper_replace(self):
        '''
        /~ operator
        '''

    def test_regexp_oper_search(self):
        '''
        ?~ operator
        '''

    def test_regexp_oper_match(self):
        '''
        =~ operator
        '''
        code = r'''
        res = []
        
        s1 = ['1', '2', '3', '']
        for n <- s1
            res <- (n, re`1|2` =~ n)
        
        s2 = ['---', 'abc', 'xyz', 'helloWorld', '1,2,3']
        for n <- s2
            res <- (n, re`[a-z]+` =~ n)
            
        s3 = ['html', '<div>', ' span <div>', '<span>']
        for n <- s3
            res <- (n, re`^<(html|div|span)>$` =~ n)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        expv = [
            ('1', True), ('2', True), ('3', False), ('', False),
            ('---', False), ('abc', True), ('xyz', True), ('helloWorld', True), ('1,2,3', False),
            ('html', False), ('<div>', True), (' span <div>', False), ('<span>', True)]
        self.assertEqual(expv, rvar.vals())



    def test_cases_split(self):
        ''' '''
        data = [
            (r're``','',''),
            (r're``miLx','', 'miLx'),
            (r're`abc`','abc',''),
            (r're`\\n\\t\s\d\w\``','\\n\\t\\s\\d\\w`',''),
            (r're`abc`ui','abc','ui'),
            (r're` \' " \'\'\' """ `mx', ' \' " \'\'\' """ ','mx'),
            (r're`abc`{fls}','abc', (VarExpr, 'fls')),
            # (r'','',''),
        ]
        cs = CaseRegexp()
        for src, expatt, exflg in data:
            tlines = splitLexems(src)
            clines:CLine = elemStream(tlines)
            rexp, subs = cs.split(clines[0].code)
            self.assertIsInstance(rexp, RegexpExpr)
            self.assertEqual(expatt, rexp.pattern)
            rflags = rexp.flags
            if isinstance(rflags, VarExpr):
                rflags = (VarExpr, rexp.flags.get().name)
            self.assertEqual(exflg, rflags)

    def test_cases_match(self):
        ''' '''
        data = [
            ('``', 0),
            ('re',0),
            ('re``',1),
            ('re""',1),
            # TODO: multiline strings
            # ('re``` ```', 1),
            # ('re""" 123"""', 1),
            ('re`123`', 1),
            ('re`[a-z]+`', 1),
            (r're`\s*[0-9a-f]`muL', 1),
            (r're`\`in back quotes\``', 1),
            (r're`\\ \\n\\t\s\d\w re-escapes`', 1),
            ('re``{fls}', 1),
            ('re`abc`{fls}', 1),
            # 'aiLmsux'
            ('re``aiLmsux', 1),
            ('re``mix', 1),
            ('re``aiLmsur', 0),
            ('re``baiLmsux', 0),
            ('re``bcdef', 0), 
            ('re`1`i mux', 0),
            ('rex``', 0),
            ('re`` ``', 0),
            ('re`` !-', 0),

        ]
        
        cs = CaseRegexp()
        for src, expe in data:
            tlines = splitLexems(src)
            clines:CLine = elemStream(tlines)
            # print(src, clines)
            self.assertEqual(bool(expe), cs.match(clines[0].code), src)

    def test_regex_combineFlags(self):
        ''' '''
        data = [
            ([], 0),
            ([256, 2, 4, 8, 16, 32, 64], 382),
            ([256], 256),
            ([2,4,32,8], 46),
            ([64, 32, 8, 16], 120),
        ]
        
        for src, exp in data:
            res = combineFlags(src)
            self.assertEqual(exp, res, 'src=%s' % str(src))

    def test_regex_str_to_flag(self):
        ''' '''
        data = [
            ('', []),
            ('aiLmsux', [256, 2, 4, 8, 16, 32, 64]),
            ('a', [256]),
            ('iLum', [2,4,32,8]),
            ('xums', [64, 32, 8, 16]),
        ]
        
        for src, exp in data:
            res = [int(n) for n in str2flags(src)]
            self.assertEqual(exp, res, 'src=%s' % src)


if __name__ == '__main__':
    main()
