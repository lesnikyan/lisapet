'''
Test of bound function / methods
'''
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



class TestBoundFuncs(TestCase):


    def test_dict_filter_k_v(self):
        ''' '''
        code = r'''
        res = []
        
        dd1 = {1:11, 2:22, 3:33, 4:44, 5:55, 6:66, -7: 77}
        res <- dd1.filter((key, val) -> key % 2 > 0 &&  key > 0)
        
        dd2 = {'a':'1', 'b':'2', 'c':'3', 'qqq':'4', 'xxx':'5', 'abc':'6'}
        res <- dd2.filter((k, v)-> k ?> 'abcd')
        res <- dd2.filter((k, v)-> v ?> '135')
        res <- dd2.filter((k, v)-> len(k) > 1 && int(v) ?> [2,4,6,8])
        
        dd3 = {'a':'abba', 'b':'baby', 33:33, 4:44, '5':55, '6':66, 7:'seven'}
        
        res <- dd3.filter((k, v)-> k :: string)
        res <- dd3.filter((k, v)-> k :: int)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            {1: 11, 3: 33, 5: 55}, 
            {'a': '1', 'b': '2', 'c': '3', 'abc': '6'}, {'a': '1', 'c': '3', 'xxx': '5'}, 
            {'qqq': '4', 'abc': '6'}, {'a': 'abba', 'b': 'baby', '5': 55, '6': 66}, 
            {33: 33, 4: 44, 7: 'seven'}]
        self.assertEqual(exv, resv)

    def test_string_upper_lower(self):
        ''' '''
        code = r'''
        res = []
        
        s1 = 'abcdef-xyz'
        res <- s1.upper()
        
        s2 = 'Hello ABCDDEF-XYZ'
        res <- s2.lower()
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = ['ABCDEF-XYZ', 'hello abcddef-xyz']
        self.assertEqual(exv, resv)

    def test_builtin_filter(self):
        ''' '''
        code = r'''
        res = []
        
        nn = [3,22,4,1,5,10,7,0]
        res <- nn.filter(x -> x < 10 && x > 1)
        
        res <- nn.filter(x -> x ?> [0, 3, 5, 7, 9])
        
        cn = list('AaBbCcDdEeXxYyZz')
        res <- cn.filter(a -> a.int() >= char_key('a') && a.int() <= char_key('z')).map(g -> string(g))
        
        struct A a:int
        
        an = [A(11), A(2), A(41), A(5), A(0), A(8)]
        res <- an.filter(a -> a.a % 2 == 0)
        
        sn = ["Hello!", "zoomba", "123", "12345", "Aaa", "aaaa", "Bbbb", "bbb", "900", "009999"]
        res <- sn.filter(s -> len(s) > 3 && s[0] !?> '0123456789')
        
        dn = [ {'a':1, 'b':2}, {'Aaa':0}, {'abc':132}, {'123':';-)'}, {'000':'zero'}, {'zope':'bd-bd-bd'}, {'q': 555}]
        res <- dn.filter(a -> len(a.keys()) == 1 && a.keys()[0][0] ?> 'aq0')
        
        # tuple
        
        ntt = (1,4,2,6,33,78,43,12,9,0)
        res <- ntt.filter(x -> x < 20).filter(y -> y > 3)
        
        stt = ('Hello','Table','house','article','Bombom','Zumma','Xenon','xxl','prima')
        res <- stt.filter(s -> s[0] ?> 'HTX')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [3, 4, 5, 7], [3, 5, 7, 0], 
            ['a', 'b', 'c', 'd', 'e', 'x', 'y', 'z'], 
            ['st@A{a: 2}', 'st@A{a: 0}', 'st@A{a: 8}'], 
            ['Hello!', 'zoomba', 'aaaa', 'Bbbb'], 
            [{'abc': 132}, {'000': 'zero'}, {'q': 555}], 
            (4, 6, 12, 9), ('Hello', 'Table', 'Xenon')]
        self.assertEqual(exv, resv)

    def test_builtin_sort(self):
        ''' '''
        code = r'''
        res = []
        
        nn = [3,2,4,1,5,0]
        res <- nn.sort((x, y) -> x - y)
        
        cn = list('dfbcae')
        res <- cn.sort((a, b) -> a.int() - b.int()).map(g -> string(g))
        
        struct A a:float
        
        an = [A(11), A(2), A(41), A(5), A(0)]
        res <- an.sort( (a, b) -> a.a - b.a)
        
        func strCompare(a, b)
            if len(a) != len(b)
                return len(a) - len(b)
            for i <- iter(len(a))
                if a[i] != b[i]
                    return a[i].int() - b[i].int()
            return 0
        
        sn = ["Hello!", "zoomba", "123", "12345", "Aaa", "aaa", "Bbb", "bbb", "900", "009"]
        res <- sn.sort(strCompare)
        
        dn = [{'Aaa':0}, {'abc':132}, {'123':';-)'}, {'000':'zero'}, {'zope':'bd-bd-bd'}, {'q': 555}]
        res <- dn.sort((a, b) -> strCompare(a.keys()[0], b.keys()[0]))
        
        ntt = (4,3,2,1,5,6,7)
        
        res <- ntt.sort((a, b)-> a - b)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [0, 1, 2, 3, 4, 5], ['a', 'b', 'c', 'd', 'e', 'f'], 
            ['st@A{a: 0.0}', 'st@A{a: 2.0}', 'st@A{a: 5.0}', 'st@A{a: 11.0}', 'st@A{a: 41.0}'], 
            ['009', '123', '900', 'Aaa', 'Bbb', 'aaa', 'bbb', '12345', 'Hello!', 'zoomba'], 
            [{'q': 555}, {'000': 'zero'}, {'123': ';-)'}, {'Aaa': 0}, {'abc': 132}, {'zope': 'bd-bd-bd'}],
            (1, 2, 3, 4, 5, 6, 7)]
        self.assertEqual(exv, resv)

    def test_type_builtin_constructors(self):
        ''' '''
        code = r'''
        res = []
        
        res <- int(1.0)
        res <- int(27 ** (1/3))
        res <- int(true)
        res <- int(false)
        res <- int(null)
        res <- int('1')
        res <- int(0x[0a 0b 0e 0f])
        res <- int(0x0a0b0e0f)
        res <- int(0x[fe dc ba 98 76 54 32 10])
        
        
        res <- float(11)
        res <- float(12.5)
        res <- float('2.5')
        res <- float(false)
        res <- float(true)
        res <- float(null)
        
        res <- bool(0)
        res <- bool(null)
        res <- bool('')
        res <- bool(float(0))
        res <- bool('false')
        res <- bool(0x[])
        res <- bool(0x[00])
        res <- bool(1)
        res <- bool('true')
        res <- bool('Hello!')
        res <- bool(0x[01])
        
        res <- bytes(4)
        res <- bytes(0x[11 22 33 4f])
        res <- bytes('Hello!')
        res <- bytes([31, 32, 41, 61])
        
        res <- string(0)
        res <- string(1)
        res <- string('')
        res <- string(null)
        res <- string([1,2,3])
        res <- string((1,2,3))
        res <- string(['','a','9'])
        res <- string(0x[])
        res <- string(0x[41 42 43 44 45])
        
        res <- list(1)
        res <- list(5)
        res <- list('Hello1')
        res <- list(0d[1 2 3 10])
        res <- list([1,2,3])
        res <- list((3,4,5))
        
        res <- tuple(1)
        res <- tuple(5)
        res <- tuple('Hello2')
        res <- tuple(0d[1 2 3 10])
        res <- tuple([1,2,3])
        res <- tuple((3,4,5))
        
        res <- dict({1:11, 2:22})
        items = [('a', 111),('b',222),('c',333)]
        res <- dict(items)
        res <- dict((['x','y','z'], [100, 200, 300]))
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            1, 3, 1, 0, 0, 1, 168496655, 168496655, 18364758544493064720, 
            11.0, 12.5, 2.5, 0.0, 1.0, 0.0, 
            False, False, False, False, False, False, False, True, True, True, True, 
            '0x[00 00 00 00]', [], '0x[48 65 6c 6c 6f 21]', '0x[1f 20 29 3d]', 
            '0', '1', '', 'null', '[1,2,3]', '(1,2,3)', "['','a','9']", '0x[]', '0x[41 42 43 44 45]', 
            [0], [0, 0, 0, 0, 0], ['g(H)', 'g(e)', 'g(l)', 'g(l)', 'g(o)', 'g(1)'], [1, 2, 3, 10], [1, 2, 3], [3, 4, 5], 
            (0,), (0, 0, 0, 0, 0), ('g(H)', 'g(e)', 'g(l)', 'g(l)', 'g(o)', 'g(2)'), (1, 2, 3, 10), (1, 2, 3), (3, 4, 5), 
            {1: 11, 2: 22}, {'a': 111, 'b': 222, 'c': 333}, {'x': 100, 'y': 200, 'z': 300}]
        self.assertEqual(exv, resv)

    def test_code_string_to_bytes(self):
        ''' '''
        code = r'''
        res = []
        
        bb = "Hello string!".bytes()
        res <- bb
        
        res <- '1 2 3 4 5'.bytes('utf8')
        
        res <- "Мама мыла раму.".bytes()
        res <- "Мама мыла раму.".bytes('cp855')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            '0x[48 65 6c 6c 6f 20 73 74 72 69 6e 67 21]', '0x[31 20 32 20 33 20 34 20 35]', 
            '0x[d0 9c d0 b0 d0 bc d0 b0 20 d0 bc d1 8b d0 bb d0 b0 20 d1 80 d0 b0 d0 bc d1 83 2e]', 
            '0x[d3 a0 d2 a0 20 d2 f1 d0 a0 20 e1 a0 d2 e7 2e]']
        self.assertEqual(exv, resv)

    def test_code_bytes_to_string(self):
        ''' '''
        code = r'''
        res = []
        
        bb1 = [31 20 32 20 33 20 34 20 35]
        res <- bb1.string('utf8')
        
        res <- [48 65 6c 6c 6f 20 62 79 74 65 73 21].string()
        
        res <- [e6 b0 b8 e6 81 92 e4 b9 8b e6 98 a5 e7 9a 84 e8 8a b1 e5 9b ad].string()
        
        res <- [c6 90 20 c6 8d 20 c6 80 20 c6 8b 20 c6 95 20 c6 a9 20 c6 b1 20 c6 b3 20 c6 9b].string()
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # to see more unicode chars: set in console:
        # >chcp 65001
        # switch font to SimSun-ExtB
        exv = ['1 2 3 4 5', 'Hello bytes!', '永恒之春的花园', 'Ɛ ƍ ƀ Ƌ ƕ Ʃ Ʊ Ƴ ƛ']
        self.assertEqual(exv, resv)

    def test_bound_each(self):
        '''
            Test method seq.each()
        '''
        code = r'''
        res = []
        
        # collect results
        func rcoll(val)
            res <- val
        
        nums1 = [1,2,3,4,5]
        res <- 'nums1'
        nums1.each(x-> rcoll(x + 100))
        
        nums2 = (11, 22, 33, 44)
        res <- 'nums2'
        nums2.each(x -> rcoll(x + 1000))
        
        dd1 = {1:11, 2:22, 3:33}
        res <- 'dd1'
        dd1.items().each(x -> (k, v = x; rcoll([k, ':', v])))
        
        res <- 'str-gen'
        [x; x <- tolist("qwerty")].each(s -> rcoll(~'<{s}>'))
        
        res <- 'str-split'
        'I am a big bug (:'.split(' ').each(s -> rcoll('%s?' << s))
        
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
        exv = [
            'nums1', 101, 102, 103, 104, 105, 
            'nums2', 1011, 1022, 1033, 1044, 
            'dd1', [1, ':', 11], [2, ':', 22], [3, ':', 33], 
            'str-gen', '<q>', '<w>', '<e>', '<r>', '<t>', '<y>', 
            'str-split', 'I?', 'am?', 'a?', 'big?', 'bug?', '(:?']
        # print('tt>',rvar.vals())
        self.assertEqual(exv, rvar.vals())

    def test_bound_methods_sequence(self):
        ''' Bound method by native function.
            Test methods of sequence: map, fold, reverse
        '''
        code = r'''
        res = []
        
        # reverse
        nums = [1,2,3]
        rnums = nums.reverse()
        res <- rnums
        res <- [1,2,3].join('^')
        
        # map
        res <- [1,2,3,4,5].map(x -> x * 11)
        func f1(x)
            ~"({x})"
        
        res <- "string1".map(f1)
        res <- "l i s t 2".split(' ').map(f1)
        res <- (1,2,3).map(x -> x * 5)
        res <- 't u p l e 3'.split(' ').map(f1)
        
        struct A a:int
        
        func si:A add(x)
            si.a += x
        
        aa = []
        for i <- [1..5]
            aa <- A(i)
        
        a2 = aa.map(val -> val.add(10))
        
        res <- a2
        
        # val from function
        func foo(n)
            [x ; x <- [0..n]]
        
        res <- foo(3).map(x -> 100 + x)
        
        # fold
        src11 = [1,2,3]
        
        func ff1(s, x)
            s + x * 10
        
        res <- src11.fold(0, ff1)
        
        src12 = [4,5,6]
        res <- src12.fold(1, (x, y) -> x * y)
        
        src13 = [7,8,9]
        res <- [7,8,9].fold('!', (s,n)-> ~"{s} {n} !")
        
        src21 = (11,22,33)
        res <- src21.fold(0, ff1)
        
        func tup22()
            (21,22,23)
        
        res <- tup22().fold(1, (x, y) -> (x * y) % 100)
        
        res <- "a b c d e f g".split(re`\s+`).fold('', (s, n) -> ~'{s} [{len(s):03d}] {n}')
        
        dds = {'a':'1001', 'b':'2002', 'c':'3003'}
        
        func dplus(dd, app:tuple)
            dd <- (app[0], toint(app[1]) - 500)
            dd

        res <- dds.items().fold([], (s, n) -> (s <- n[0]; s <- n[1]; s))
        res <- dds.items().fold({}, (s, n) -> dplus(s, n))
        res <- dds.items().fold({}, (s, n) -> ( v= n[1]+'_val' ; s <- (n[0], v) ;s))
        
        res <- dds.items().fold({}, (s, n) -> (s <- (n[1], n[0]) ; s))
        dds['a'] = '7007'
        res <- dds.items().fold({}, (s, n) -> (s <- n.reverse() ; s))
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        
        rvar = ctx.get('res').get()
        exv = [
            [3, 2, 1], '1^2^3', [11, 22, 33, 44, 55], '(s)(t)(r)(i)(n)(g)(1)', ['(l)', '(i)', '(s)', '(t)', '(2)'], 
            (5, 10, 15), ['(t)', '(u)', '(p)', '(l)', '(e)', '(3)'], [11, 12, 13, 14, 15], 
            [100, 101, 102, 103], 60, 120, '! 7 ! 8 ! 9 !', 660, 26, 
            ' [000] a [008] b [016] c [024] d [032] e [040] f [048] g', ['a', '1001', 'b', '2002', 'c', '3003'], 
            {'a': 501, 'b': 1502, 'c': 2503}, {'a': '1001_val', 'b': '2002_val', 'c': '3003_val'}, 
            {'1001': 'a', '2002': 'b', '3003': 'c'}, {'7007': 'a', '2002': 'b', '3003': 'c'}]
        # print('tt>',rvar.vals())
        self.assertEqual(exv, rvar.vals())

    def test_bound_native_methods(self):
        ''' Bound method by native function.
        bind : str_split(_, src, sep)
        as a `stringVal.split(sep)`
        >>
        src = "a,b,c"
        src.split(',') # > ['a', 'b', 'c']
        '''
        code = r'''
        res = []
        
        # list methods
        nums = [1,2,3]
        rnums = nums.reverse()
        res <- rnums
        res <- [1,2,3].join('^')
        
        # dict methods
        kc = 'c'
        dk = {1:11, 2:22, 'a':'aaa', 'b':'bbb', kc: 'ccc'}
        ks = dk.keys()
        res <- ks
        
        res <- dk.items()
        
        # split
        str1 = 'aa-bb-cc'
        rsplit = str1.split('-')
        res <- rsplit
        res <- "d,e,f".split(',')
        res <- "here12many54hidden09words".split(re`[0-9]+`)
        
        # split by ampty separator is a converting to list of shortest parts
        res <- 'Hello 123!'.split('')
        
        # join
        ss = ['s1', 's2', 's3']
        res <- '-'.join(ss)
        res <- "_".join(['s4','s5','s6'])
        res <- "/".join(['s7','s8', 's9'])
        res <- `"`.join((11,12,13))
        
        mstr_splitted = """
        aaa
        bbb
        ccc
        """.split('\n')[1:-1]
        
        res <- mstr_splitted
        
        # combo
        wds = 'Hello dear friend'.split(' ').map(w -> ~"<t>{w}</t>").join(' ')
        res <- wds
        
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
        exv = [
            [3, 2, 1], '1^2^3', [1, 2, 'a', 'b', 'c'], 
            [(1, 11), (2, 22), ('a', 'aaa'), ('b', 'bbb'), ('c', 'ccc')], 
            ['aa', 'bb', 'cc'], ['d', 'e', 'f'], ['here', 'many', 'hidden', 'words'], ['H', 'e', 'l', 'l', 'o', ' ', '1', '2', '3', '!'],
            's1-s2-s3', 's4_s5_s6', 's7/s8/s9', '11"12"13', ['aaa', 'bbb', 'ccc'], '<t>Hello</t> <t>dear</t> <t>friend</t>']
        self.assertEqual(exv, rvar.vals())

    def test_builtin_len_for_string(self):
        ''' test implementation of builtin function len for string type '''
        code = r'''
        nn = [
            '', ' ', '123', 'a b c'
        ]
        nn <- """abc
        def"""
        res = []
        for s <- nn
            res <- len(s)
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        self.assertEqual([0, 1, 3, 5, 7], rvar.vals())

    def test_built_foldl(self):
        ''' '''
        code = r'''
        res = 0
        
        func sum(nums)
            plus = (x, y) -> x + y
            foldl(0, nums, plus)
        
        # args = [1,2,3,4,5]
        s1 = sum([1,2,3,4,5])
        s2 = sum([1..10])
        s3 = sum([x ** 2 ; x <- [2..9]])
        
        res = [s1, s2, s3]
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        self.assertEqual([15, 55, 284], rval.vals())

    def test_dict_func_ditems(self):
        ''' '''
        code = r'''
        res = []
        src = [
            {}, {1:11}, {2:22, 3:33},
            {'a':'a11'}, {'bb':'b22','cc':'c33','dd':'d44'}, 
            {'nums' : [1,2,3]}, {'names' : ['Adam','Bob','Cindy']}
        ]
        
        for dd <- src
            kvs = ditems(dd)
            res <- (dd, kvs)
        
        
        # print('\n'); for r <- res /: print(r)
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
        exv = [
            ({}, []), ({1: 11}, [(1, 11)]), ({2: 22, 3: 33}, [(2, 22), (3, 33)]), 
            ({'a': 'a11'}, [('a', 'a11')]), ({'bb': 'b22', 'cc': 'c33', 'dd': 'd44'}, [('bb', 'b22'), ('cc', 'c33'), ('dd', 'd44')]), 
            ({'nums': [1, 2, 3]}, [('nums', [1, 2, 3])]), ({'names': ['Adam', 'Bob', 'Cindy']}, [('names', ['Adam', 'Bob', 'Cindy'])])]
        self.assertEqual(exv, rvar.vals())

    def test_dict_func_dkeys(self):
        ''' '''
        code = r'''
        res = []
        src = [
            {}, {1:11}, {2:22, 3:33},
            {'a':'a11'}, {'bb':'b22','cc':'c33','dd':'d44'}, 
        ]
        
        for dd <- src
            kk = dkeys(dd)
            res <- (dd, kk)
        
        
        # print('\n'); for r <- res /: print(r)
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
        exv = [
            ({}, []), ({1: 11}, [1]), ({2: 22, 3: 33}, [2, 3]), 
            ({'a': 'a11'}, ['a']), 
            ({'bb': 'b22', 'cc': 'c33', 'dd': 'd44'}, ['bb', 'cc', 'dd'])]
        self.assertEqual(exv, rvar.vals())

    def test_tostr(self):
        ''' '''
        code = r'''
        
        struct A a:int
        struct B(A) b:string 
        
        func foo(x)
            x + 10
        
        res = []
        src = [
            1, 0, 500, null, true, false,
            "", `\ \n \t \s \d \w \b {} ' " `,
            'abc', ' "a" ', " 'b' ", 
            [], [1,2,3], (1,2,3), {1:2, 'a':'b'},
            [1,2,3,4,5], [(x, 10*x) ; x <- [10..20]],
            [{('k'+tostr(x)) : x * 101} ; x <- [21..29]],
            ['a', 'b'], ['"a b c"', '"'], ["'d e f'", "'", "'\"'"],
            A(11), A{}, B{a:22,b:"barro"},
            [A(33)], (B{a:44, b:"55"},), {'aa':A(66), 'bb':B(0,'b77')},
        ]
        delems = {}
        for i <- [5..16]
            delems <- ('p'+tostr(i), i * 202)
        src <- delems
        
        for s <- src
            res <- tostr(s)
        
        # print('\n'); for r <- res /: print(r)
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
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            '1', '0', '500', 'null', 'true', 'false', '', '\\ \\n \\t \\s \\d \\w \\b {} \' " ', 
            'abc', ' "a" ', " 'b' ", '[]', '[1,2,3]', '(1,2,3)', "{'1':2,'a':'b'}", '[1,2,3,4,5]', 
            '[(10,100),(11,110),(12,120),(13,130),(14,140),(15,150),(16,160),(17,170),(18,180),(19,190),(20,200)]', 
            "[{'k21':2121},{'k22':2222},{'k23':2323},{'k24':2424},{'k25':2525},{'k26':2626},{'k27':2727},{'k28':2828},{'k29':2929}]", 
            "['a','b']", '[\'"a b c"\',\'"\']', '["\'d e f\'","\'","\'\\"\'"]', 
            'st@A{a: 11}', 'st@A{a: 0}', 'st@B{a: 22, b: barro}', "['st@A{a: 33}']", 
            "('st@B{a: 44, b: 55}')", "{'aa':'st@A{a: 66}','bb':'st@B{a: 0, b: b77}'}", 
            "{'p5':1010,'p6':1212,'p7':1414,'p8':1616,'p9':1818,'p10':2020,'p11':2222,'p12':2424,'p13':2626,'p14':2828,'p15':3030,'p16':3232}"]
        exv = [
            '1', '0', '500', 'null', 'true', 'false', '', '\\ \\n \\t \\s \\d \\w \\b {} \' " ', 
            'abc', ' "a" ', " 'b' ", '[]', '[1,2,3]', '(1,2,3)', "{'1':2,'a':'b'}", '[1,2,3,4,5]', 
            '[(10,100),(11,110),(12,120),(13,130),(14,140),(15,150),(16,160),(17,170),(18,180),(19,190),(20,200)]', 
            "[{'k21':2121},{'k22':2222},{'k23':2323},{'k24':2424},{'k25':2525},{'k26':2626},{'k27':2727},{'k28':2828},{'k29':2929}]", 
            "['a','b']", '[\'"a b c"\',\'"\']', '["\'d e f\'","\'","\'\\"\'"]', 
            'st@A{a: 11}', 'st@A{a: 0}', "st@B{a: 22, b: 'barro'}", "['st@A{a: 33}']", 
            '("st@B{a: 44, b: \'55\'}")', '{\'aa\':\'st@A{a: 66}\',\'bb\':"st@B{a: 0, b: \'b77\'}"}', 
            "{'p5':1010,'p6':1212,'p7':1414,'p8':1616,'p9':1818,'p10':2020,'p11':2222,'p12':2424,'p13':2626,'p14':2828,'p15':3030,'p16':3232}"]
        self.assertEqual(exv, resv)

    def test_builtin_split_join_replace(self):
        ''' '''
        code = r'''
        res = []
        
        src1 = "red,green,blue"
        
        res <- split(src1, ',')
        
        src2 = ['hello','dear','string']
        
        res <- join(src2, '_')
        
        src3 = "<div>Hello replace</div>"
        
        res <- replace(src3, 'div', 'span')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # rvar = ctx.get('res')
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exp = [['red', 'green', 'blue'], 'hello_dear_string', '<span>Hello replace</span>']
        self.assertEqual(exp, rvar.vals())


if __name__ == '__main__':
    main()
