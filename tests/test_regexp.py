

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

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *
from libs.regexp import *
from cases.operwords import *



class TestRegexp(TestCase):
    ''' Test builtin regexp lib. '''


    def test_regexp_replace(self):
        ''' replace(src, rx, repl) '''
        code = r'''
        res = []
        
        src1 = '11-1-1, 22=2-2, 33/3/3'
        r1 = replace(src1, re`[\-=/]`, ':')
        res <- r1
        
        src2 = 'a111 b222 c333'
        r2 = replace(src2, re`([a-z])(\d+)`i, `<\1:\2:\1>`)
        res <- r2
        
        src3 = 'Tom Red works hard. Elise Orange singing more. Ben Grayhold lying on sofa.'
        r3 = replace(src3, re`([A-Z][a-z]+)\s+([A-Z][a-z]+)`, '<person fname="\\1" sname="\\2">')
        res <- r3
        
        # print(res)
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
            '11:1:1, 22:2:2, 33:3:3', '<a:111:a> <b:222:b> <c:333:c>', 
            '<person fname="Tom" sname="Red"> works hard. '
            '<person fname="Elise" sname="Orange"> singing more. '
            '<person fname="Ben" sname="Grayhold"> lying on sofa.']
        self.assertEqual(expv, rvar.vals())

    def test_regexp_split(self):
        ''' split(string, Regexp) '''
        code = r'''
        src = """a11 b22,c33
        d44;d45
        e55|f66    g77 h88 i99 /j101-k202--n204
        """
        parts = split(src, re`[\s\n\t\|/;,-]+`)
        res = []
        for s <- parts
            res <- ~'<{s}>'
        
        # print('parts:', parts)
        # print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        expv = ['<a11>', '<b22>', '<c33>', '<d44>', '<d45>', '<e55>', '<f66>',
                '<g77>', '<h88>', '<i99>', '<j101>', '<k202>', '<n204>']
        self.assertEqual(expv, rvar.vals())

    def test_regexp_oper_search_for(self):
        ''' loop by rx ?~ results '''
        
        code = r'''
        src = """
        a11 b22 c33
        d44
        e55 f66 g77 h88 i99 j101 k202 
        """
        res = []
        
        for s <- re`\w(\d+)`m ?~ src
            res <- (s, s[1])
            # print(s)
        # print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        expv = [(['a11', '11'], '11'), (['b22', '22'], '22'), (['c33', '33'], '33'),
            (['d44', '44'], '44'), (['e55', '55'], '55'), (['f66', '66'], '66'),
            (['g77', '77'], '77'), (['h88', '88'], '88'), (['i99', '99'], '99'),
            (['j101', '101'], '101'), (['k202', '202'], '202')]
        self.assertEqual(expv, rvar.vals())

    def test_regexp_oper_search(self):
        '''
        ?~ operator
        '''
        code = r'''
        res = []
        
        # empty result []
        s0 = ['', '  ', '1 2 3', 'a s d']
        for n <- s0
            res <- ('>0', n, re`\w{2,}` ?~ n)
        
        # one result [['...']]
        s1 = [' 12', ' 123 ', 'asd', 'asd123']
        for n <- s1
            res <- ('>1', n, re`\w{2,}` ?~ n)
        
        # one result with groups[['','','']]
        s2 = ['1q01', '2Ww022', '3Ee345 ', '4Rrfv567 432']
        for n <- s2
            rx = re`\d([a-z]+)(\d+)`i
            res <- ('>2', n, rx ?~ n)
            
        # several results [[''],['']]
        s3 = ['1a11 2bbb 3eab a44fff 5remember 6beep',]
        for n <- s3
            rx = re`\d[a-f]+`
            res <- ('>3', n, rx ?~ n)
            
        # several results with groups [['',''],['','']]
        s4 = [
            'John Tompson 111-22-33, Cat Morris 122-23-24',
            '1-2-3 11-22-33 111-222-333',
            '0-0-0 1-1-1 2-2-2 1111111111-222222222222-3333333333',
        ]
        for n <- s4
            rx = re`(\d+)\-(\d+)\-(\d+)`
            fres = rx ?~ n
            res <- ('>4', n, fres)
        
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
        expv = [('>0', '', []), ('>0', '  ', []), ('>0', '1 2 3', []), ('>0', 'a s d', []), 
                ('>1', ' 12', [['12']]), ('>1', ' 123 ', [['123']]), ('>1', 'asd', [['asd']]), ('>1', 'asd123', [['asd123']]), 
                ('>2', '1q01', [['1q01', 'q', '01']]), ('>2', '2Ww022', [['2Ww022', 'Ww', '022']]), 
                ('>2', '3Ee345 ', [['3Ee345', 'Ee', '345']]), ('>2', '4Rrfv567 432', [['4Rrfv567', 'Rrfv', '567']]), 
                ('>3', '1a11 2bbb 3eab a44fff 5remember 6beep', [['1a'], ['2bbb'], ['3eab'], ['4fff'], ['6bee']]), 
                ('>4', 'John Tompson 111-22-33, Cat Morris 122-23-24', [['111-22-33', '111', '22', '33'], ['122-23-24', '122', '23', '24']]), 
                ('>4', '1-2-3 11-22-33 111-222-333', [['1-2-3', '1', '2', '3'], ['11-22-33', '11', '22', '33'], ['111-222-333', '111', '222', '333']]), 
                ('>4', '0-0-0 1-1-1 2-2-2 1111111111-222222222222-3333333333', 
                 [['0-0-0', '0', '0', '0'], ['1-1-1', '1', '1', '1'], ['2-2-2', '2', '2', '2'], 
                  ['1111111111-222222222222-3333333333', '1111111111', '222222222222', '3333333333']])]
        self.assertEqual(expv, rvar.vals())

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



    def test_re_parsing_CaseRegexp_split(self):
        ''' '''
        data = [
            (r're``','',''),
            (r're``miLx','', 'miLx'),
            (r're`abc`','abc',''),
            (r're`\n\t\s\d\w \` \' \" `','\\n\\t\\s\\d\\w ` \\\' \\" ',''),
            (r're`abc`ui','abc','ui'),
            ('re` \' " \'\'\' """ `mx', ' \' " \'\'\' """ ','mx'),
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

    def test_re_parsing_CaseRegexp_match(self):
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
