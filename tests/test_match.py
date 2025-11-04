

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


    def test_match_struct(self):
        ''' pattern of struct, including collections in fields. '''
        code = r'''
        
        struct Type1 a:int, b:int
        struct TypeA color:string
        struct TypeB(TypeA) name:string, age:int
        struct TypeC nums:list, a:int
        struct TypeD fd:dict, fl:list, ft:tuple
        
        nn = [
            Type1{},  #  empty construtor
            Type1(10, 20), Type1(10, 0), Type1(10, 2), Type1(1, 2),
            TypeA('000'), TypeA('fff'),
            
            TypeB{color:'fff', name:'Aaa', age:44},
            TypeB{color:'red', name:'Bimbo', age:22},
            TypeB{},  #  empty constructor when inheritance
            TypeB{color:'green', name:'Ambo', age:33},
            
            TypeC{nums:[], a:1}, TypeC{nums:[331], a:2}, TypeC{nums:[34, 35, 36], a:3}, 
            TypeD({'a':111}, [], (,)), TypeD({}, [22,33,44], (,)), TypeD({'x':1111}, [2222], (3333,)), 
            TypeD({}, [], (555,)), TypeD({}, [], (61,62,63,64)), TypeD({}, [], (,)), 
            TypeD{},  #  empty constructor with collections in fields 
        ]
        res = []
        
        
        for n <- nn
            match n
                Type1{b:0} !- res <- [n, 10]
                Type1{a:10, b:20} !- res <- [n, 11]
                Type1{a:10} !- res <- [n, 12]
                Type1{} !- res <- [n, 19]
                TypeA{color:'fff'} !- res <- [n, 23]
                TypeB{name:name, age:22} !- res <- [n, (name), 21]
                TypeB{color:''} !- res <- [n, 27]
                TypeB{name:name, color:color} !- res <- [n, (name, color), 28]
                TypeA{} !- res <- [n, 29]
                TypeC{nums:[]} !- res <- [n, 30]
                TypeC{nums:[331]} !- res <- [n, 31]
                TypeC{nums:[a, b, c]} !- res <- [n, (a,b,c), 32]
                TypeD{fd:{'a':aval,*}} !- res <- [n, (aval,), 41]
                TypeD{fl:[a, b, *]} !- res <- [n, (a,b), 42]
                TypeD{ft:(a), fd:{b:c}, fl:[d]} !- res <- [n, (a,b,c,d), 43]
                TypeD{ft:(a,*)} !- res <- [n, (a,), 44]
                TypeD{} !- res <- [n, 49]
                _ !- res <- [n, 2999]
            # print('nres:', res)
        # 
        print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        
        exp = [
            ['st@Type1{a: 0,b: 0}', 10], ['st@Type1{a: 10,b: 20}', 11], ['st@Type1{a: 10,b: 0}', 10], ['st@Type1{a: 10,b: 2}', 12], ['st@Type1{a: 1,b: 2}', 19], 
            ['st@TypeA{color: 000}', 29], ['st@TypeA{color: fff}', 23], ['st@TypeB{name: Aaa,age: 44}', 23], 
            ['st@TypeB{name: Bimbo,age: 22}', 'Bimbo', 21], ['st@TypeB{name: ,age: 0}', 27], ['st@TypeB{name: Ambo,age: 33}', ('Ambo', 'green'), 28], 
            ['st@TypeC{nums: [],a: 1}', 30], ['st@TypeC{nums: [331],a: 2}', 31], ['st@TypeC{nums: [34, 35, 36],a: 3}', (34, 35, 36), 32], 
            ["st@TypeD{fd: {'a': 111},fl: [],ft: ()}", (111,), 41], ['st@TypeD{fd: {},fl: [22, 33, 44],ft: ()}', (22, 33), 42], 
            ["st@TypeD{fd: {'x': 1111},fl: [2222],ft: (3333,)}", (3333, 'x', 1111, 2222), 43], ['st@TypeD{fd: {},fl: [],ft: (555,)}', (555,), 44], 
            ['st@TypeD{fd: {},fl: [],ft: (61, 62, 63, 64)}', (61,), 44], ['st@TypeD{fd: {},fl: [],ft: ()}', 49], ['st@TypeD{fd: {},fl: [],ft: ()}', 49]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_pattern_post_guard(self):
        '''
        post-guard in matching case
        match n
            pattern :? guard !- ...
        '''
        code = '''
        nn = [
            101, 2, 3, 4, 
            [11,12], [4,3], (5,1), (1,7,5), [1,2,1,2,1,2,7],
            {1:11}, {2:22, 222:222}, {3:33, 33:333, 333:3333},
            (1, 2, 3), (11, 12, 15),
            ]
        res = []
        
        for n <- nn
            match n
                101 :? 2 > 3 !- res <- [n, 'n0'] # should be skipped
                101 :? 2 < 3 !- res <- [n, 'n1']
                [a, b] :? a > b !- res <- [n, (a, b), 'n2']
                (a, _) | [_,a] :? a > 2 !- res <- [n, (a, ), 'n3']
                [*] | (*) :? 7 ?> n !- res <- [n, 'n7']
                {*} :? len(n) > 1 !- res <- [n, 'n52']
                {a:b} :? b > 8 !- res <- [n, (a, b), 'n51']
                1 |2 |3 :? n ?> [2, 3]  !- res <- [n, 'n61']
                (a, b, c) :? d = 16; c < d !- res <- [n, (a, b, c, d), 'n53']
                _  !- res <- [n, 999]
        
        # print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [[101, 'n1'], [2, 'n61'], [3, 'n61'], [4, 999], 
            [[11, 12], (12,), 'n3'], [[4, 3], (4, 3), 'n2'], [(5, 1), (5,), 'n3'], 
            [{1: 11}, (1, 11), 'n51'], [{2: 22, 222: 222}, 'n52'], [{3: 33, 33: 333, 333: 3333}, 'n52']
        ]
        # self.assertEqual(exp, rvar.vals())

    def test_multicase_simple(self):
        '''
        Multipattern as set of cases:
        each of sub case is valid
        match n
            1 | 2 | 3 !- ...
        '''
        code = '''
        nn = [
            1,2,3,4,5,6,
            (7,), (18,28),
            [9], [11, 12],
            {1:11}, {2:22, 3:33}, 
            {4:44, 44:444, 55:555}, 4444
            ]
        res = []
        
        for n <- nn
            match n
                1 !- res <- [n, 11]
                2 | 3 !- res <- [n, 22]
                4 | 5 | 6 !- res <- [n, 33]
                (_) | [_] | {_:_} !- res <- [n, 101]
                (a, *) | [a, *] | {a:_, _:_} !- res <- [n, (a,), 102]
                {*} | 4444 !- res <- [n, 103]
                _  !- res <- [n, 999]
        
        # print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [[1, 11], [2, 22], [3, 22], [4, 33], [5, 33], [6, 33], 
               [(7,), 101], [(18, 28), (18,), 102], [[9], 101], [[11, 12], (11,), 102], 
               [{1: 11}, 101], [{2: 22, 3: 33}, (2,), 102], [{4: 44, 44: 444, 55: 555}, 103], [4444, 103]]
        self.assertEqual(exp, rvar.vals())

    def test_match_tuple_star(self):
        ''' '''
        code = r'''
        
        nn = [
            (2,), (11,2), 
            (41, 42), (11, 12, 41, 42), (42, 41, 42, 11, 12),
            (11, 12, 41, 13, 14, 15, 42), (11, 12, 41, 13, 42, 14, 15, 15, 15),
            (11,12,9,13,14,19,31, 32), (11,12,9,13,14,19,20),
            (11, 12, 13, 9, 111, 1112, 1113, 1114, 19, 201, 202, 203, 204),
        ]
        res = []
        
        for n <- nn
            match n
                [*, 2]   !- res <- [n, 1021]
                (*, 2)   !- res <- [n, 21]
                (?, *, 41, ?, *, 42, ?, *)   !- res <- [n, 41]
                (a, _, ?,  9, *, b, c, 19, _, ?, *, d)   !- res <- [n, (a, b, c, d), 91]
                (a, _, ?,  9, *, b, c, 19, _, ?, *)   !- res <- [n, (a, b, c), 92]
                [*]      !- res <- [n, 1099]
                (*)      !- res <- [n, 99]
                _ !- res <- [n, 5999]
            # print(res)
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
            [[2], 21], [[11, 2], 21],
            [[41, 42], 41], [[11, 12, 41, 42], 41], [[42, 41, 42, 11, 12], 41], 
            [[11, 12, 41, 13, 14, 15, 42], 41], [[11, 12, 41, 13, 42, 14, 15, 15, 15], 41], 
             [[11, 12, 9, 13, 14, 19, 31, 32], (11, 13, 14, 32), 91], [[11, 12, 9, 13, 14, 19, 20], (11, 13, 14), 92], 
             [[11, 12, 13, 9, 111, 1112, 1113, 1114, 19, 201, 202, 203, 204], (11, 1113, 1114, 204), 91]
        ]
        exp = [
            [(2,), 21], [(11, 2), 21], 
            [(41, 42), 41], [(11, 12, 41, 42), 41], [(42, 41, 42, 11, 12), 41], [(11, 12, 41, 13, 14, 15, 42), 41], [(11, 12, 41, 13, 42, 14, 15, 15, 15), 41], 
            [(11, 12, 9, 13, 14, 19, 31, 32), (11, 13, 14, 32), 91], [(11, 12, 9, 13, 14, 19, 20), (11, 13, 14), 92], 
            [(11, 12, 13, 9, 111, 1112, 1113, 1114, 19, 201, 202, 203, 204), (11, 1113, 1114, 204), 91]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_list_star(self):
        ''' '''
        code = r'''
        
        nn = [
            [], [1], [1,11], 
            [2], [11,2], 
            [3], [11,3], [11, 12, 3], [11, 12, 3, 14],
            [41, 42], [11, 12, 41, 42], [42, 41, 42, 11, 12],
            [11, 12, 41, 13, 14, 15, 42], [11, 12, 41, 13, 42, 14, 15, 15, 15],
            [11 , 5], [11, 12, 5], [11, 111, 1111, 12, 5], [11, 5, 12, 13], [5], [5, 11, 12],
            [11, 6, 61], [11, 12, 6, 13, 61], 
            [11, 7], [111, 12, 7], [111, 12, 13, 7, 14, 15],
            [11, 12, 8, 13], [11, 12, 13, 8, 14, 15],
            [11,12,9,13,14,19,31, 32], [11,12,9,13,14,19,20],
            [11, 12, 13, 9, 111, 1112, 1113, 1114, 19, 201, 202, 203, 204],
        ]
        res = []
        
        for n <- nn
            match n
                [*, 2]   !- res <- [n, 21]
                [?, *, 3, *]   !- res <- [n, 31]
                [?, *, 41, ?, *, 42, ?, *]   !- res <- [n, 41]
                [_, 5, *]   !- res <- [n, 51]
                [*, _, 5]   !- res <- [n, 52]
                [5, *]   !- res <- [n, 53]
                [_, ?, 6, *, 61]   !- res <- [n, 61]
                
                [a, *, 7, *]   !- res <- [n,a, 71]
                [*, a, _, 8, b, *]   !- res <- [n, (a, b), 81]
                [a, _, ?,  9, *, b, c, 19, _, ?, *, d]   !- res <- [n, (a, b, c, d), 91]
                [a, _, ?,  9, *, b, c, 19, _, ?, *]   !- res <- [n, (a, b, c), 92]
                
                [*]      !- res <- [n, 99]
                _ !- res <- [n, 5999]
            # print(res)
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
            [[], 99], [[1], 99], [[1, 11], 99], [[2], 21], [[11, 2], 21],
            [[3], 31], [[11, 3], 31], [[11, 12, 3], 31], [[11, 12, 3, 14], 31], 
            [[41, 42], 41], [[11, 12, 41, 42], 41], [[42, 41, 42, 11, 12], 41], 
            [[11, 12, 41, 13, 14, 15, 42], 41], [[11, 12, 41, 13, 42, 14, 15, 15, 15], 41], 
            [[11, 5], 51], [[11, 12, 5], 52], [[11, 111, 1111, 12, 5], 52], [[11, 5, 12, 13], 51], [[5], 53], [[5, 11, 12], 53], 
            [[11, 6, 61], 61], [[11, 12, 6, 13, 61], 61], 
            [[11, 7], 11, 71], [[111, 12, 7], 111, 71], [[111, 12, 13, 7, 14, 15], 111, 71], 
            [[11, 12, 8, 13], (11, 13), 81], [[11, 12, 13, 8, 14, 15], (12, 14), 81], 
             [[11, 12, 9, 13, 14, 19, 31, 32], (11, 13, 14, 32), 91], [[11, 12, 9, 13, 14, 19, 20], (11, 13, 14), 92], 
             [[11, 12, 13, 9, 111, 1112, 1113, 1114, 19, 201, 202, 203, 204], (11, 1113, 1114, 204), 91]
        ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_tuple_maybe(self):
        ''' '''
        code = r'''
        
        nn = [
            (,), (1,), (2,),
            (1,7), (1,2), (11,12,7),
            (5,5,5), (5,6,7), (4,5,6), (5,15),
            (3,4,5), (3, 3, 3), (3,123),
            (1,2,3), (1,3),
            (1,2,3,4,5), (1,2,3,5), (1,2,5), (1,5),
            (1,6), (1,2,6), (1,2,3,4,5,6),
            (1,2,3,7), (1,2,13,14,15,7), (1,2,3,4,5,7), (1,2,3,4,5,6,7),
        ]
        res = []
        
        for n <- nn
            match n
                (?, 2) !- res <- [n, 22]
                (?, 5,?) !- res <- [n, 53]
                (_, 5, ?) !- res <- [n, 54]
                (5, ?, ?) !- res <- [n, 55]
                (?) !- res <- [n, 11]
                (1, ?, 3) !- res <- [n, 31]
                (1, ?, ?, ?, 5) !- res <- [n, 51]
                (3,_,?) !- res <- [n, 32]
                (?, ?, ?, ?, a, 6) !- res <- [n, a, 61]
                (x, ?, ?, 4, ?, b, 7) !- res <- [n, (x,b), 71]
                (x, ?, ?, ?, a, b, 7) !- res <- [n, (x,a,b), 72]
                (x, ?, 7) !- res <- [n, (x), 73]
                _ !- res <- [n, 3999]
            # print(res)
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
        
        exp = [[tuple(), 11], [(1,), 11], [(2,), 22], [(1, 7), 1, 73], [(1, 2), 22], [(11, 12, 7), 11, 73],
               [(5, 5, 5), 54], [(5, 6, 7), 55], [(4, 5, 6), 53], [(5, 15), 53],
               [(3, 4, 5), 32], [(3, 3, 3), 32], [(3, 123), 32], [(1, 2, 3), 31], [(1, 3), 31],
               [(1, 2, 3, 4, 5), 51], [(1, 2, 3, 5), 51], [(1, 2, 5), 51], [(1, 5), 53],
               [(1, 6), 1, 61], [(1, 2, 6), 2, 61], [(1, 2, 3, 4, 5, 6), 5, 61],
               [(1, 2, 3, 7), (1, 2, 3), 72], [(1, 2, 13, 14, 15, 7), (1, 14, 15), 72],
               [(1, 2, 3, 4, 5, 7), (1, 5), 71], [(1, 2, 3, 4, 5, 6, 7), (1, 6), 71]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_list_maybe(self):
        ''' '''
        code = r'''
        
        nn = [
            [], [1], [2],
            [1,7], [1,2], [11,12,7],
            [5,5,5], [5,6,7], [4,5,6], [5,15],
            [3,4,5], [3, 3, 3], [3,123],
            [1,2,3], [1,3],
            [1,2,3,4,5], [1,2,3,5], [1,2,5], [1,5],
            [1,6], [1,2,6], [1,2,3,4,5,6],
            [11,12,7], [1,2,3,7], [1,2,13,14,15,7], [1,2,3,4,5,7], [1,2,3,4,5,6,7],
        ]
        res = []
        
        for n <- nn
            match n
                [?, 2] !- res <- [n, 22]
                [?, 5,?] !- res <- [n, 53]
                [_, 5, ?] !- res <- [n, 54]
                [5, ?, ?] !- res <- [n, 55]
                [?] !- res <- [n, 11]
                [1, ?, 3] !- res <- [n, 31]
                [1, ?, ?, ?, 5] !- res <- [n, 51]
                [3,_,?] !- res <- [n, 32]
                [?, ?, ?, ?, a, 6] !- res <- [n, a, 61]
                [x, ?, ?, 4, ?, b, 7] !- res <- [n, (x,b), 71]
                [x, ?, ?, ?, a, b, 7] !- res <- [n, (x,a,b), 72]
                [x, ?, 7] !- res <- [n, (x), 73]
                _ !- res <- [n, 3999]
            # print(res)
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
        exp = [[[], 11], [[1], 11], [[2], 22], 
               [[1, 7], 1, 73], [[1, 2], 22], [[11, 12, 7], 11, 73], 
               [[5, 5, 5], 54], [[5, 6, 7], 55], [[4, 5, 6], 53], [[5, 15], 53], 
               [[3, 4, 5], 32], [[3, 3, 3], 32], [[3, 123], 32], [[1, 2, 3], 31], 
               [[1, 3], 31], [[1, 2, 3, 4, 5], 51], [[1, 2, 3, 5], 51], [[1, 2, 5], 51], [[1, 5], 53], 
               [[1, 6], 1, 61], [[1, 2, 6], 2, 61], [[1, 2, 3, 4, 5, 6], 5, 61], 
               [[11, 12, 7], 11, 73], [[1, 2, 3, 7], (1, 2, 3), 72], [[1, 2, 13, 14, 15, 7], (1, 14, 15), 72], 
               [[1, 2, 3, 4, 5, 7], (1, 5), 71], [[1, 2, 3, 4, 5, 6, 7], (1, 6), 71]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

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
