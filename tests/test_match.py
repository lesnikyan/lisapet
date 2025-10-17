

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext, moduleContext

from strformat import *


from tests.utils import *



class TestMatch(TestCase):
    ''' cases of `match` statement '''



    def test_match_dict_maybe(self):
        ''' q-mark as a maybe-element '''
        code = r'''
        
        nn = [
            1, [], {},
            {'1':'111'}, {'a':'1'}, {'c':'2'}, {'b':'3'}, {'t':5}, 
            {'c':'1', 'a':'2'}, # 'a' on 2-nd pos in code. should be matched by {'a':_, ?}
            {'b':'3', 'c':'2'}, 
            {'c':'3', 'd':'2'}, 
            {'a':'122', 'z':'', 'x':'333'}, 
            {'b':'122', 'z':'', 'c':'335'}, 
            {'b':'122', 'z':'', 'c':'335', 'v':'336'}, 
            {'a':'122', 'z':'', 'x':'', 'c':'444'},
            {'a':'122', 'z':'', 'x':'', 'c':'', 'v':'555'},
            {'a':'122', 'z':'', 'x':'', 'c':'', 'v':'', 'b':'666'},
            {'a':'122', 'z':'', 'x':'', 'c':'', 'v':'', 'b':'', 'n':'777'},
            {'r':'122', 'z':'', 'x':'', 'c':'', 'v':'', 'b':'', 'n':'777'},
            
        ]
        res = []
        
        for n <- nn
            match n
                {'a':_, ?} !- res <- [n, 12]
                {'b':v, ?} !- res <- [n, 13]
                {?} !- res <- [n, 11] # put here because it will eat empty and 1-pair cases
                {_:v, ?} !- res <- [n, 14] #  2-pairs and longer will reach here
                {'a':v, ?,?} !- res <- [n, 15] # a + possible 2
                {'b':v, ?,?, 'c':_} !- res <- [n, 16]
                {'a':v, ?,?,?,?} !- res <- [n, 17] # a + possible 4 elems
                {'a':v, *} !- res <- [n, 18] # a + more than 4 elems
                {'a':v, ?,?,?,?, *} !- res <- [n, 19] # the same as prev
                {*} !- res <- [n, 20]
                _ !- res <- [n, 3999]
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # print('TT>>')
        exp = [[1, 3999], [[], 3999], [{}, 11], 
               [{'1': '111'}, 11], [{'a': '1'}, 12], [{'c': '2'}, 11], [{'b': '3'}, 13], [{'t': 5}, 11], 
               [{'c': '1', 'a': '2'}, 12], [{'b': '3', 'c': '2'}, 13], [{'c': '3', 'd': '2'}, 14], 
               [{'a': '122', 'z': '', 'x': '333'}, 15], 
               [{'b': '122', 'z': '', 'c': '335'}, 16], [{'b': '122', 'z': '', 'c': '335', 'v': '336'}, 16],
               [{'a': '122', 'z': '', 'x': '', 'c': '444'}, 17], 
               [{'a': '122', 'z': '', 'x': '', 'c': '', 'v': '555'}, 17], 
               [{'a': '122', 'z': '', 'x': '', 'c': '', 'v': '', 'b': '666'}, 18], 
               [{'a': '122', 'z': '', 'x': '', 'c': '', 'v': '', 'b': '', 'n': '777'}, 18], 
               [{'r': '122', 'z': '', 'x': '', 'c': '', 'v': '', 'b': '', 'n': '777'}, 20]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_dict_star(self):
        ''' * as an any elements '''
        code = r'''
        
        nn = [
            1,(,), [], {},
            {'a':''}, {'b':''}, {'c':''},
            {'a':'', 'b':''}, {'a':'', 'c':''}, {'d':'', 'e':'_n1'},  {'d':'11', 'e':'22'}, 
            {'a':'', '1':'', '2':'', '3':''}, {'b':'', '1':'', '2':'', '3':''},  
            {'a':'', 'b':'', 'c':'', '1':'', '2':'', '3':'', '4':'', '5':''}, 
        ]
        res = []
        
        for n <- nn
            match n
                {'a':v} !- res <- [n, 12]
                {'a':v1, 'b': v2, *} !- res <- [n, 21]
                {'a':v1, 'c': v2, *} !- res <- [n, 22]
                {'a':v, *} !- res <- [n, 23]
                {k:v, _:_, _:_, *} !- res <- [n, 24]
                {k:v} !- res <- [n, 25]
                {k:'_n1', *} !- res <- [n, 26]
                {*} !- res <- [n, 30]
                _ !- res <- [n, 3999]
        
        # print('res = ', res)
        '''

        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[1, 3999], [(), 3999], [[], 3999], [{}, 30], [{'a': ''}, 12], [{'b': ''}, 25], [{'c': ''}, 25], 
               [{'a': '', 'b': ''}, 21], [{'a': '', 'c': ''}, 22], [{'d': '', 'e': '_n1'}, 26], [{'d': '11', 'e': '22'}, 30],
               [{'a': '', '1': '', '2': '', '3': ''}, 23], [{'b': '', '1': '', '2': '', '3': ''}, 24],
               [{'a': '', 'b': '', 'c': '', '1': '', '2': '', '3': '', '4': '', '5': ''}, 21]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_dict_other(self):
        ''' '''
        code = r'''
        
        nn = [
            {'aa':11}, {'bb':22}, {'aa':'33'}, {'aa3':'43'},
            {'aa':'-33','bb':'-44'}, {'aa':'-33','dd':'-44'},  
            {'aaa':'-33','ee':'-44'}, {'77':'-77', '88':'-88'}, 
            {'a1':'_011','a2':'_022','a3':'_033'}, 
            {'b1':'_111', 'b2':'_122', 'b3':'_133'}, {'c1':'211', 'c2':'222', 'c3':'233'}, 
            {'d1':'__3', 'd2':'__2', 'd3':'__1'}, 
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                {'bb':v} !- res <- [n, v, 18]
                {k:'33'} !- res <- [n, 19]
                {k:v} !- res <- [n, (k,v), 21]
                {'aa':v1, 'bb':v2} !- res <- [n, (v1, v2), 22]
                {'aa':v1, _:v2} !- res <- [n, 23]
                {_:v1, 'ee':v2} !- res <- [n, (v1,v2), 25]
                {'77': val, _:_} !- res <- [n, 27]
                {a:b, c:d} !- res <- [n, 28]
                {'a1':v1, 'a2':v2, _:v3} !- res <- [n, 31]
                {'b2':v2, 'b3':v3, _:v1} !- res <- [n, 32]
                {'c3':v3, k2:'222', k1:v1} !- res <- [n, 33]
                {a:'__1', b:c, _:_} !- res <- [n, 335] # doubtful case, value of key in dict is not unique
                {a:b, c:d, e:f} !- res <- [n, 36]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[{'aa': 11}, ('aa', 11), 21], [{'bb': 22}, 22, 18], [{'aa': '33'}, 19], [{'aa3': '43'}, ('aa3', '43'), 21],
               [{'aa': '-33', 'bb': '-44'}, ('-33', '-44'), 22], [{'aa': '-33', 'dd': '-44'}, 23], [{'aaa': '-33', 'ee': '-44'}, ('-33', '-44'), 25],
               [{'77': '-77', '88': '-88'}, 27], [{'a1': '_011', 'a2': '_022', 'a3': '_033'}, 31], [{'b1': '_111', 'b2': '_122', 'b3': '_133'}, 32],
               [{'c1': '211', 'c2': '222', 'c3': '233'}, 33], [{'d1': '__3', 'd2': '__2', 'd3': '__1'}, 335]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_dict_empty_cases(self):
        ''' '''
        code = r'''
        
        nn = [
            {'':''}, {'_':'100'}, {' ':101}, {0:102},
            {'':'-11',' ':'-22'},
            {'66':'-66', null:'-67'},
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                {0:_} !- res <- [n, 19]
                {'':_} !- res <- [n, 20]
                {' ':_} !- res <- [n, 21]
                {'_':v} !- res <- [n, (v,), 22]
                {k:v} !- res <- [n, (k,v), 23]
                {null:v, _:_} !- res <- [n, 25]
                {'':v, _:_} !- res <- [n, 26]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[{'': ''}, 20], [{'_': '100'}, ('100',), 22], [{' ': 101}, 21], [{0: 102}, 19],
               [{'': '-11', ' ': '-22'}, 26], [{'66': '-66', Null(): '-67'}, 25]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_dict_base(self):
        ''' '''
        code = r'''
        
        nn = [
            1, (,), [], {},
            {1:10}, {'aa':11}, {'bb':22}, {'cc':'33'},
            {'a1':'_011','a2':'_022','a3':'_033'}
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                () !- res <- [n, 11]
                [] !- res <-   [n, 12]
                {} !- res <- [n, 13]
                {1:_} !- res <- [n, 16] # num key
                {'aa':_} !- res <- [n, 17] # str key
                {k:'33'} !- res <- [n, 19] # key va and str val
                {_:_} !- res <- [n, 21] # any : any
                {'aa':v1, _:_} !- res <- [n, 23] # 2 pairs
                {'a1':v1, 'a2':v2, _:v3} !- res <- [n, 31] # 3 pairs, 2 key vals
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[1, 2999], [(), 11], [[], 12], [{}, 13], [{1: 10}, 16],
               [{'aa': 11}, 17], [{'bb': 22}, 21], [{'cc': '33'}, 19],
               [{'a1': '_011', 'a2': '_022', 'a3': '_033'}, 31]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())


    def test_match_tuple_vars(self):
        ''' '''
        code = r'''
        
        nn = [(,), (1,), (2,), (7),  
            (1,2), (1,7), (7,2),(111,222),
            (11,3,22), (1,2,3), (1,3,7),(111,222,333),
            1
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                () !- res <- [n, 11]
                (2) !- res <- [n, 11]
                (a) !- res <-   [n, (a,), 12]
                (_) !- res <- [n, 19] # shouldn't be used because prev
                (a,2) !- res <- [n, (a,), 13]
                (a,b) !- res <- [n, (a,b), 14]
                (a,_,3) !- res <- [n, (a,), 21]
                (a,b,22) !- res <- [n, (a,b), 222]
                (a,b,c) !- res <- [n, (a,b,c), 26]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[tuple(), 11], [(1,), (1,), 12],
               [(1, 2), (1,), 13], [(1, 7), (1, 7), 14], 
               [(11, 3, 22), (11, 3), 23], [(1, 2, 3), (1,), 23], 
               [1, 2999]
        ]
        exp = [[(), 11], [(1,), (1,), 12], [(2,), 11], [7, 2999], 
               [(1, 2), (1,), 13], [(1, 7), (1, 7), 14], [(7, 2), (7,), 13], [(111, 222), (111, 222), 14], 
               [(11, 3, 22), (11, 3), 222], [(1, 2, 3), (1,), 21], [(1, 3, 7), (1, 3, 7), 26], [(111, 222, 333), (111, 222, 333), 26], [1, 2999]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_list_vars(self):
        ''' '''
        code = r'''
        
        nn = [[], 
            [1], [1,2], [1,7],
            [7], [7,2],[111,222],
            [11,3,22], [1,2,3], [1,3,7], [111,222,333],
            1
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                [] !- res <- [n, 11]
                [a] !- res <-   [n, (a,), 12]
                [_] !- res <- [n, 19] # shouldn't be used because prev
                [a,2] !- res <- [n, (a,), 13]
                [a,b] !- res <- [n, (a,b), 14]
                [a,_,1] !- res <- [n, (a,), 23]
                [a,_,3] !- res <- [n, (a,), 23]
                [a,b,22] !- res <- [n, (a,b), 23]
                [a,b,c] !- res <- [n, (a,b,c), 26]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[[], 11], [[1], (1,), 12], 
               [[1, 2], (1,), 13], [[1, 7], (1, 7), 14], [[7], (7,), 12], [[7, 2], (7,), 13], [[111, 222], (111, 222), 14], 
               [[11, 3, 22], (11, 3), 23], [[1, 2, 3], (1,), 23], [[1, 3, 7], (1, 3, 7), 26], [[111, 222, 333], (111, 222, 333), 26],
               [1, 2999]
        ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_tuple_vals_and_underscore(self):
        ''' '''
        code = r'''
        # nn=[2]
        nn = [(,), (1,), (1,7), (1,2), 
            (7,), (7,20), (111,222), (1,3,7), (111,222,333),
            1
        ]
        res = []
        
        # print('nn:', nn)
        for n <- nn
            # print('nn:', n)
            match n
                # 1 !- 1
                () !- res <- [n, 101]
                (1) !- res <-   [n, 102]
                (1,7) !- res <- [n, 103]
                (_) !- res <- [n, 201]
                (1,_) !- res <- [n, 202]
                (_,2) !- res <- [n, 203]
                (_,_) !- res <- [n, 204]
                (1,_,7) !- res <- [n, 205]
                (_,_,_) !- res <- [n, 206]
                _ !- res <- [n, 20999]

            # print('nres:', res)

        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[tuple(),101], [(1,), 102], [(1, 7), 103], [(1, 2), 202], [(7,), 201], 
               [(7, 20), 204], [(111, 222), 204], [(1, 3, 7), 205], [(111, 222, 333), 206], 
                [1, 20999]
        ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_list_strvals(self):
        ''' '''
        code = r'''
        
        nn = [
            [], [1], 
            ['1'], ['2'], [`a`],["bb"], [`ccc`],
            ['',""], ['a','bb'], ['aa','cc'], ['a','_'], ['a','_abc'], 
            ['','',''],
            'a', 1
        ]
        # nn = [['', '', '']]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                [] !- res <- [n, 11]
                ['1'] !- res <-   [n, 12]
                ['a'] !- res <- [n, 13]
                ['bb'] !- res <- [n, 14]
                ['','',''] !- res <- [n, 15]
                ['a','bb'] !- res <- [n, 16]
                ['aa','cc'] !- res <- [n, 17]
                ['aaa','_'] !- res <- [n, 18]
                ['a',_] !- res <- [n, 19]
                [a, b] !- res <- [n, (a,b), 20]
                [_] !- res <- [n, 21]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [
            [[], 11], [[1], 21], 
            [['1'], 12], [['2'], 21], [['a'], 13], [['bb'], 14], [['ccc'], 21],
            [['', ''], ('', ''), 20], [['a', 'bb'], 16], [['aa', 'cc'], 17], 
            [['a', '_'], 19], [['a', '_abc'], 19], 
            [['', '', ''], 15], ['a', 2999], [1, 2999]
            ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_list_vals_and_underscore(self):
        ''' '''
        code = r'''
        
        nn = [[], [1], [1,7], [1,2], 
            [7], [7,2],[111,222],[1,3,7],[111,222,333],
            1
        ]
        res = []
        
        for n <- nn
            # print('nn:', n)
            match n
                # 1 !- 1
                [] !- res <- [n, 11]
                [1] !- res <-   [n, 12]
                [1,7] !- res <- [n, 13]
                [_] !- res <- [n, 21]
                [1,_] !- res <- [n, 22]
                [_,2] !- res <- [n, 23]
                [_,_] !- res <- [n, 24]
                [1,_,7] !- res <- [n, 25]
                [_,_,_] !- res <- [n, 26]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[[], 11], [[1], 12], [[1, 7], 13], 
               [[1, 2], 22], [[7], 21], [[7, 2], 23], [[111, 222], 24], 
               [[1, 3, 7], 25], [[111, 222, 333], 26],
                [1, 2999]
        ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_strings(self):
        ''' '''
        code = r'''
        
        ss = [' ', 'aaa', 'bbb', 'bcd', '123', '']
        res = []
        
        for s <- ss
            match s
                '' !-      res <- [s, 1]
                ' ' !-      res <- [s, 2]
                'aaa' !-   res <- [s, 3]
                'b' !-     res <- [s, 4]
                'bcd' !-   res <- [s, 5]
                '123' !-   res <- [s, 123]
                _ !-
                    res <- [s, 1000]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        # print('..tt>')
        ex.do(ctx)
        exp = [[' ', 2], ['aaa', 3], ['bbb', 1000], ['bcd', 5], ['123', 123], ['', 1]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())
    

    def test_basic_match(self):
        ''' '''
        code = r'''
        
        nn = [1,2,3, 1]
        res = []
        
        for n <- nn
            match n
                1 !- res <- [n,111]
                2 !- res <- [n,222]
                _ !- res <- [n,999]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[1, 111], [2, 222], [3, 999], [1, 111]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def _test_match_var_case(self):
        '''
        TODO: do we need var as a pattern?
        '''
        code = '''
        a = 4
        r1 = 0
        b = 3
        match a
            1  !- r1 = 100
            10 !- r1 = 200
            b  !- r1 = 300
            _  !- r1 = -2
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        exp.do(ctx)
        r1 = ctx.get('r1').get()
        dprint('#t >>> r:', r1)

    def test_match_for_if_lambda(self):
        ''' TODO: match with for loop, `if` statement in the same case line '''
        code = r'''
        c = 5
        res = 0
        func foo2(ff)
            ff(11)
        rrs = [] # [0 ; x <- [0..11]]
        ff = x -> x * 10
        for i <- [0..8]
            # print('i:', i)
            res = 1
            t = i + 10
            match i
                1 !- res = 10
                2 !- 
                    if res > 0 && res < 4
                        # print('c2', i, res)
                        res *= 11 * i
                3 !- res = foo2(x -> x ** 2)
                4 !- f = x -> x * 12
                    res = f(i)
                5 !- res = foo2(ff) + i
                6 !- 
                    for j <- [0..5]
                        # print('c5', j, res)
                        res += i
                7 !- 
                    for j = 1; j < 6; j = j + 1
                        # print('c7', j, res)
                        res *= j
                8 !- 
                    if c= t + 100; c > 110 && t > 4
                        # print('c2', i, res)
                        res = c
                _ !- res = 1001
            rrs <- res

        # print('rrs = ', rrs)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('rrs').get()
        self.assertEqual([1001, 10, 22, 121, 48, 115, 37, 120, 118], rvar.vals())


    def test_CaseMatchSub_match(self):
        cs = CaseMatchCase()
        rrs = []
        def checkRes(code, exp):
            dprint('$$ run test ------------------')
            dprint('CODE:','\n'+code)
            # code = lines[0]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = cs.match(elems)
            dprint('#tt >>> ', code, res)
            msg = 'Tried use code: %s' % code
            if exp:
                self.assertTrue(res, msg)
            else:
                self.assertFalse(res, msg)
            
        src = ''''
        val !- expr
        123 !- a + b
        234 !- r = 2 + 3
        3 !- res = 4
        user(123) !- res
        '''
        src = norm(src[1:].rstrip())
        data = src.splitlines()
        for code in data:
            if code.strip() == '':
                continue
            checkRes(code, True)
        
        src = ''''
        val 123 -> expr
        1,2,3 -> a + b
        x <- src
        -> expr ...
        user(123) + 0 -> res
        '''
        src = norm(src[1:].rstrip())
        data = src.splitlines()
        for code in data:
            if code.strip() == '':
                continue
            checkRes(code, False)


if __name__ == '__main__':
    main()
