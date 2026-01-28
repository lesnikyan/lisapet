

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext, moduleContext

from bases.strformat import *


from tests.utils import *



class TestMatch(TestCase):
    ''' cases of `match` statement '''





    def test_refactored_match_case_blocks(self):
        ''' check refactored sub-block of match-case, test fixed return from if in loop'''
        code = r'''
        res = []
        
        struct A
        
        func fbase(n)
            match n
                # indent block
                ::int # some comment
                    x  = 1
                    return x
                
                # inline block
                ::bool /: x = 2; return x
                
                # /: but indent (it's ok)
                {_:_} /:
                    y = 3
                    return y
                
                # block with sub control
                p::(tuple|list)
                    r4 = []
                    for x <- p
                        r4 <- x
                        if len(r4) >= 3
                            return (4, r4, p)
                # default
                _ /: return 5
            -1000
        
        nn = [1, true, [1,2,3], (3,4,5), {4:44}, 1.5, [100]]
        
        for k <- nn
            res <- fbase(k)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [1, 2, (4, [1, 2, 3], [1, 2, 3]), (4, [3, 4, 5], (3, 4, 5)), 3, 5, -1000]
        self.assertEqual(exv, rvar.vals())

    def test_match_pattern_multitype_no_var(self):
        ''' multitype in no-var pattern `::(int|B)` '''
        code = r'''
        res = [-111]
        
        struct A a:int
        struct B b:int
        struct C c:string
        struct D
        struct BB(B) bb:int
        
        struct AA n:int
        struct BBB n:int
        struct CC n:int
        struct DD n:int
        struct EE n:int
        
        struct FF n:int
        struct GG n:int
        struct HH n:int
        struct JJ n:int
        
        nn = [1, 1.1, true, [1], (1,2), 'asd', {1:11, 2:22}, 
            A{}, B{}, C{}, D{}, [A{}, B{}], [A{}, C{}], 
            BB{}, (A{}, BB{}), (A{}, C{}),
            AA{n:1}, BBB{n:2}, CC{n:3}, DD{n:4}, EE{n:5},
            (AA(6), CC(7)), (FF(8), DD(9)),
            FF(11), GG(12), HH(13), JJ(14),
            AA(22), GG(24)]
            
        for n <- nn
            match n
                :: (int|float) /: res <- 1
                n :: (A|B) /: res <- 4
                n :: (C|bool) /: res <- 5
                [::A, ::(B|C)] /: res <- 7
                (::A, ::(B|C)) /: res <- 8
                ::(AA|GG) :? n.n ?> [22,23,24] /: res <- 500 + n.n
                ::(FF|GG) | ::(HH|JJ) /: res <- 300 + n.n
                (::AA, ::CC) | (::FF, ::DD) /: res <- (400 + n[0].n, 400 + n[1].n)
                :: (string|list) /: res <- 2
                :: (dict|tuple) /: res <- 3
                :: (string|list|D) | :: dict /: res <- 6
                ::(AA|BBB|CC|DD|EE) /: res <- 200 + n.n
                _ /: res <- 199
        
        # print('res = ', res)
        '''
        
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [-111, 1, 1, 5, 2, 3, 2, 3, 4, 4, 5, 6, 7, 7, 4, 8, 8,
               201, 202, 203, 204, 205,
               (406, 407), (408, 409), 311, 312, 313, 314, 522, 524]
        self.assertEqual(exv, rvar.vals())

    def test_multitype_match_pattern(self):
        ''' '''
        code = r'''
        res = [0]
        
        struct A a:int
        struct B b:int
        struct C c:string
        struct D
        struct BB(B) bb:int
        
        n = A{}
        nn = [1, 1.1, true, [1], (1,2), 'asd', {1:11, 2:22}, 
            A{}, B{}, C{}, D{}, [A{}, B{}], [A{}, C{}], 
            BB{}, (A{}, BB{}), (A{}, C{}),]
            
        for n <- nn
            match n
                n :: (int|float) /: res <- 1
                n :: (A|B) /: res <- 4
                n :: (C|bool) /: res <- 5
                [a::A, b::(B|C)] /: res <- 7
                (a::A, b::(B|C)) /: res <- 8
                n :: (string|list) /: res <- 2
                n :: (dict|tuple) /: res <- 3
                n :: (string|list|D) | n :: dict /: res <- 6
                _ /: res <- 199
        # (int|list|bool)
        # print('res = ', res)
        '''
        
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [0, 1, 1, 5, 2, 3, 2, 3, 4, 4, 5, 6, 7, 7, 4, 8, 8]
        self.assertEqual(exv, rvar.vals())

    def test_novar_type_struct(self):
        ''' :: A '''
        code = r'''
        res = [0]
        
        struct A a:int
        struct B b:int
        struct C c:string
        struct D
        struct BB(B) bb:int
        
        nn = [
            A{}, B{}, C{}, D{}, BB{},
            [A{}, B{}], [A{}, BB{}], [C{}, D{}], 
            [C{}, C{}], [A{}, A{}], [D{}],
        ]
        
        for n <- nn
            match n
                :: A /: res <- 10
                :: B /: res <- 11
                :: C | ::D /: res <- 12
                [:: A, ::B] | [::C, ::D] /: res <- 13
                [_{}, _{}]     /: res <- 14
                _ /: res <- 999
        
        # print('res = ', res)
        '''
        
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [0, 10, 11, 12, 12, 11, 13, 13, 13, 14, 14, 999]
        self.assertEqual(exv, rvar.vals())

    def test_match_pattern_type_structs(self):
        ''' '''
        code = r'''
        res = [-111]
        
        struct A a:int
        struct B b:int
        struct C c:string
        struct D
        struct BB(B) bb:int
        
        nn = [
            A{}, B{}, C('cat'), D(),
            [A{}, B{}], (A{}, C{}), [A{}, BB{}],
            [A{}, A{}], [D{}, D{}],[D{}, B{}],
            {11:A{}, 22:B{}}, {33:C{}, 44:BB{}}, {34:A{}, 45:BB{}}, 
        ]
        
        for n <- nn
            match n
                a :: A /: res <- (10 , n, a)
                :: B /: res <- (11 , n)
                ::C | ::D /: res <- (16 , n)
                [a::A, b::(B)] /: res <- (12 , n, a, b)
                (a::A, b::(C)) /: res <- (13 , n, a, b)
                [a::D, _{}] /: res <- (15 , n, a)
                [_{}, _{}]     /: res <- (14 , n)
                {k1: a::A, k2: b::B} /: res <- (18, n, k1, k2, a, b)
                ::dict /: res <- (17, n)
                _ /: res <- (999 , n)

        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            -111, (10, 'st@A{a: 0}', 'st@A{a: 0}'), (11, 'st@B{b: 0}'), (16, 'st@C{c: cat}'), (16, 'st@D{}'), 
            (12, ['st@A{a: 0}', 'st@B{b: 0}'], 'st@A{a: 0}', 'st@B{b: 0}'), (13, ('st@A{a: 0}', 'st@C{c: }'), 'st@A{a: 0}', 'st@C{c: }'), 
            (12, ['st@A{a: 0}', 'st@BB{b: 0,bb: 0}'], 'st@A{a: 0}', 'st@BB{b: 0,bb: 0}'), (14, ['st@A{a: 0}', 'st@A{a: 0}']), 
            (15, ['st@D{}', 'st@D{}'], 'st@D{}'), (15, ['st@D{}', 'st@B{b: 0}'], 'st@D{}'), 
            (18, {11: 'st@A{a: 0}', 22: 'st@B{b: 0}'}, 11, 22, 'st@A{a: 0}', 'st@B{b: 0}'), 
            (17, {33: 'st@C{c: }', 44: 'st@BB{b: 0,bb: 0}'}), 
            (18, {34: 'st@A{a: 0}', 45: 'st@BB{b: 0,bb: 0}'}, 34, 45, 'st@A{a: 0}', 'st@BB{b: 0,bb: 0}')]
        self.assertEqual(exv, rvar.vals())

    def test_match_mixed_with_regexp(self):
        '''  '''
        code = r'''
        res = []
        
        struct A a1:string
        struct B(A) b1: string
        
        nns = [
            # [], (,), {},
            ["abc"], ("werq",), ["327"], ("010",), ["0xfed"],
            ["56473829","amba"], ('samba', 'salsa'), 
            {"xyz":1}, {"0xfde":0xfd0},
            ["Napoleon543"], ({"Napoleon123": 1002}, "napo@bumbum.es"),
            {"Red line": "alert", "Green place":"rest"}, {"Green tree": "yield", "Red wine":"drink"}, 
            A("<div>"), A("<xml>"), A('ggg'),
            B('', '123'), B{a1:'feed', b1:'abc'}, B{a1:'food', b1:'abc'}, 
            [A('xxx')],
        ]
        for nn <- nns
            match nn
                [re`[a-d]+`] | (re`[qwerty]+`) /: res <- (nn, 1)
                [re`[\d+]+`] | (re`[0-3]+`) | [re`0x[0-9a-f]{2,}`] /: res <- (nn, 2)
                [re`^[\d+]+$`, re`.+`] | (re`^[a-z]+$`, re`^[^\s]+$`)  /: res <- (nn, 3)
                [re`[w-z]+`] | (re`[w-z]+`) | {re`[w-z]+`:_}  /: res <- (nn, 4)
                {re`.+`:1} /: res <- (nn, 5)
                {re`0x[\d0-f]+$`:_} /: res <- (nn, 51)
                {re`^Red.+$`: a:: string, re`^Green.+$`: b:: string} /: res <- (nn, (a, b), 52)
                [re'Napo.+'] | ({re`Napo[a-z]+\d+` : ::int}, re`\w+@\w+\.\w`) /: res <- (nn, 61)
                
                B{b1:re`\d+`} /: res <- (nn, 71)
                B{a1:re`^[a-f]+$`} /: res <- (nn, 72)
                A{a1:re`<(?:html|div|span)>`} /: res <- [nn, 73]
                _{a1:re`g+`} /: res <- (nn, 74)
                B{} /: res <- (nn, 701)
                A{} /: res <- (nn, 702)
                [A{a1:re`x+`}] /: res <- (nn, 75)
                
                [*] /: res <- (nn, 881)
                (*) /: res <- (nn, 882)
                {*}  /: res <- (nn, 883)
                _ /: res <- (nn, 999)
        
        # print('>>\n')
        # for n <- res /: print('', (n,))
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
        null = Null()
        expv = [
            (['abc'], 1), (('werq',), 1), (['327'], 2), (('010',), 2), (['0xfed'], 2), 
            (['56473829', 'amba'], 3), (('samba', 'salsa'), 3), ({'xyz': 1}, 4), 
            ({'0xfde': 4048}, 51), (['Napoleon543'], 61), (({'Napoleon123': 1002}, 'napo@bumbum.es'), 61), 
            ({'Red line': 'alert', 'Green place': 'rest'}, ('alert', 'rest'), 52), 
            ({'Green tree': 'yield', 'Red wine': 'drink'}, ('drink', 'yield'), 52), 
            ['st@A{a1: <div>}', 73], ('st@A{a1: <xml>}', 702), ('st@A{a1: ggg}', 74), ('st@B{a1: ,b1: 123}', 71), 
            ('st@B{a1: feed,b1: abc}', 72), ('st@B{a1: food,b1: abc}', 701), (['st@A{a1: xxx}'], 75)]
        self.assertEqual(expv, rvar.vals())

    def test_match_type_in_collections(self):
        ''' test match
            [::int, b::int]
            (::int, ::string)
            {k::string : val::list}
        '''
        code = r'''
        res = []
        
        func foo(x)
            2 * x
        
        m3 = x -> x * 3
        
        nns = [ 
            [111, 112], ["", "ab"], [false, 22, 3.3], [1.0, "acbd", true],
            [(1,2,3)], ["4", (4,)], 
            (11,), (true,), (false,), (1, 2.5, 0 == 0), ("", "abba"),
            ((1,1), []), ("5", [5]), ([],),
            {'s': 11}, {12:"c1"}, {15:16}, {22:33}, 
            {'aa':'bb', 23:35}, {111:14, 'qwerty':15}, {11:101, 12:102}, 
            {'aaa':'bbb', 32:34, 15:17},
            {'ak' : [1,2,3]}, {'bk':(3,4,5)}, 
            {'ck':{21:23}}, {'ee':{'q':897}, 45: {32:34}},
            {'foo': foo}, [foo, m3, (x -> x * 7)]
        ]
        for nn <- nns
            match nn
                [x, a::int] /: res <- (nn, (x, a), '[int, int]', 11)
                [::string, b :: string] /: res <- (nn, (b,), '[string, string]', 12)
                [::bool, ::int, ::float] /: res <- (nn, '[bool, int, float]', 13)
                [a::float, b :: string, c :: bool] /: res <- (nn, (a,b,c), '[float, string, bool]', 14)
                
                [a::tuple] /: res <- (nn, (a,), '[tuple]', 15)
                [::string, ::tuple] /: res <- (nn, '[strn, tuple]', 16)
                
                (::int) /: res <- (nn, '(int)', 20)
                (x::bool) /: res <- (nn, ('x:', x), '(bool)', 21)
                (::int, ::float, ::bool) /: res <- (nn, '(int, float, bool)', 22)
                (a::int, b::float, c::bool, d::string) /: res <- (nn, '(int, float, bool, string)', 23)
                (a::string, b::string) /: res <- (nn, 'strn, strn', 24)
                [a :: tuple, b::list] /: res <- (nn, [a, b], '(tuple, list)', 25)
                (a::string, b::list) /: res <- (nn, '(strn, list)', 26)
                (::list) /: res <- (nn, '(list)', 27)
                
                {key::string : vv::int} /: res <- (nn, (key, vv), '{}', 30)
                {k :: int : 'c1'} /: res <- (nn, '{k::int : "c1" }', 31)
                {15 : b::int} /: res <- (nn, (b,), '{15: b::int}', 32)
                {a : ::int} /: res <- (nn, (a,), '{a:int}', 33)
                
                {::int : 14, _: :: int} /: res <- (nn, '{}', 34)
                {::string : ::string, ::int : ::int} /: res <- (nn, '{}', 35)
                {11:v1, ::int : v2} /: res <- (nn, (v1, v2), '{11:v1, int:v2}', 36)
                {a::string : b::string, c::int : d::int, 15:17}
                    res <- (nn, (a, b, c, d), '{a::string : b::string, c::int : d::int, 15:17}', 37)
                {a: ::list} /: res <- (nn, (a,), '{}', 37)
                {a: b::tuple} /: res <- (nn, '{}', 38)
                {a: b::dict} /: res <- (nn, (a, b,), '{}', 39)
                {a::int : b::dict, c: {'q':d}} /: res <- (nn, (a, b, c, d), '{}', 391)
                {a::string : f1::function} /: 
                    b = f1(5)
                    res <- ('f1', (a, b,), '{a::string : f1::function}', 40)
                
                [f1::function, f2::function, f3::function] /: 
                    rr = [f(11) ; f <- [f1, f2, f3]]
                    res <- ('f,f,f', rr, '[f1::function, f2::function, f3::function]', 41)
                
                _ /: res <- (nn, 999)
        
        # print('>>\n')
        # for n <- res /: print(n)
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
        null = Null()
        expv = [
            ([111, 112], (111, 112), '[int, int]', 11), (['', 'ab'], ('ab',), '[string, string]', 12), ([False, 22, 3.3], '[bool, int, float]', 13), 
            ([1.0, 'acbd', True], (1.0, 'acbd', True), '[float, string, bool]', 14), ([(1, 2, 3)], ((1, 2, 3),), '[tuple]', 15), 
            (['4', (4,)], '[strn, tuple]', 16), ((11,), '(int)', 20), ((True,), ('x:', True), '(bool)', 21), 
            ((False,), ('x:', False), '(bool)', 21), ((1, 2.5, True), '(int, float, bool)', 22), (('', 'abba'), 'strn, strn', 24),
            (((1, 1), []), 999), (('5', [5]), '(strn, list)', 26), (([],), '(list)', 27), ({'s': 11}, ('s', 11), '{}', 30), 
            ({12: 'c1'}, '{k::int : "c1" }', 31), ({15: 16}, (16,), '{15: b::int}', 32), ({22: 33}, (22,), '{a:int}', 33), 
            ({'aa': 'bb', 23: 35}, '{}', 35), ({111: 14, 'qwerty': 15}, '{}', 34), ({11: 101, 12: 102}, (101, 102), '{11:v1, int:v2}', 36), 
            ({'aaa': 'bbb', 32: 34, 15: 17}, ('aaa', 'bbb', 32, 34), '{a::string : b::string, c::int : d::int, 15:17}', 37), 
            ({'ak': [1, 2, 3]}, ('ak',), '{}', 37), ({'bk': (3, 4, 5)}, '{}', 38), ({'ck': {21: 23}}, ('ck', {21: 23}), '{}', 39), 
            ({'ee': {'q': 897}, 45: {32: 34}}, (45, {32: 34}, 'ee', 897), '{}', 391), ('f1', ('foo', 10), '{a::string : f1::function}', 40), 
            ('f,f,f', [22, 33, 77], '[f1::function, f2::function, f3::function]', 41)]
        self.assertEqual(expv, rvar.vals())

    def test_match_case_by_typed_vals(self):
        ''' test match var :: int /: '''
        code = r'''
        res = []
        
        func foo(x)
            2 * x
        
        m3 = x -> x * 3
        
        nns = [
            1, 1.5, true, 
            "abc", [3], (4,5), {6:7},
            foo, m3, (x -> x * 5)
        ]
        for nn <- nns
            match nn
                a::int /: res <- (nn, 'int', 11)
                a::float /: res <- (nn, 'float', 12)
                a::bool /: res <- (nn, 'bool', 13)
                a::string /: res <- (nn, 'string', 21)
                a:: list /: res <- (nn, 'list', 22)
                a:: dict /: res <- (nn, 'dict', 23)
                a:: tuple /: res <- (nn, 'tuple', 24)
                a:: function 
                    fres = [nn(x) ; x <- [17, 20]]
                    res <- (fres, 'function', 25)
                _ /: res <- (nn, 999)
        
        # print(res)
        # for n <- res /: print(n)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        null = Null()
        expv = [(1, 'int', 11), (1.5, 'float', 12), (True, 'bool', 13), ('abc', 'string', 21), 
                ([3], 'list', 22), ((4, 5), 'tuple', 24), ({6: 7}, 'dict', 23), 
                ([34, 40], 'function', 25), ([51, 60], 'function', 25), ([85, 100], 'function', 25)]
        self.assertEqual(expv, rvar.vals())

    def test_match_case_by_type_simple(self):
        ''' test match ::int /: '''
        code = r'''
        res = []
        
        func foo(x)
            2 * x
        
        m3 = x -> x * 3
        
        nns = [
            1, 1.5, true, 
            "abc", [3], (4,5), {6:7},
            foo, m3, (x -> x * 5)
        ]
        for nn <- nns
            match nn
                ::int /: res <- (nn, 'int', 11)
                ::float /: res <- (nn, 'float', 12)
                ::bool /: res <- (nn, 'bool', 13)
                ::string /: res <- (nn, 'string', 21)
                :: list /: res <- (nn, 'list', 22)
                :: dict /: res <- (nn, 'dict', 23)
                :: tuple /: res <- (nn, 'tuple', 24)
                :: function
                    fres = [nn(x) ; x <- [7, 10]]
                    res <- (fres, 'function', 25)
                _ /: res <- (nn, 999)
        
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
        null = Null()
        expv = [(1, 'int', 11), (1.5, 'float', 12), (True, 'bool', 13), ('abc', 'string', 21), 
                ([3], 'list', 22), ((4, 5), 'tuple', 24), ({6: 7}, 'dict', 23), 
                ([14, 20], 'function', 25), ([21, 30], 'function', 25), ([35, 50], 'function', 25)]
        self.assertEqual(expv, rvar.vals())


    def test_match_mixed_nested(self):
        '''  '''
        code = r'''
        res = []
        
        struct A a1:int
        struct B(A) b1: int
        struct C c1:string
        
        
        nns = [
            '', null, 0, false, (,), {}, [], 
            [(,), (,)], ([],[]), [{}, {}], ({}, {}),
            {1:[], 2:[]}, {1:(,), 2:(,)},
            [{5:5}, {}], [{5:5}, {6:7, 8:9}], 
            ({7:7}, {}, ), ({7:7}, {8:9, 11:22}), 
            [{1:[(,), (,)], 2:[(,), (,)]}, {3:[(,), (,)], 4:[(,), (,)]}], 
            [{1:(,)}], ({1:[]},), [{1:22}], [({1:33},)], ([{1:[44]}],),
            [A(11)], [A(11), 1], [(A{}, 11), (B{}, 22)],
            (A(11),), ([A(12), B(0, 13)], [B(0, 14), C('015')]),
            {'a':A{}, 'b':B{}}, {'a':A(22), 'b':B(0,33)},
        ]
        
        for nn <- nns
            match nn
                [(), ()] /: res <- (nn, 1)
                ([], []) /: res <- (nn, 2)
                [{}, {}] /: res <- (nn, 3)
                ({}, {}) /: res <- (nn, 4)
                
                [(1), (*)] /: res <- (nn, 5)
                ([3], [*]) /: res <- (nn, 6)
                [{5:5}, {*}] /: res <- (nn, 7)
                ({7:7}, {*}) /: res <- (nn, 8)
                
                {1:[], 2:[]} /: res <- (nn, 9)
                {1:(), 2:()} /: res <- (nn, 10)
                
                [{1:[(), ()], 2:[(), ()]}, {3:[(), ()], 4:[(), ()]}] /: res <- (nn, 11)
                [{1:()}] /: res <- (nn, 12)
                ({1:[]}) /: res <- (nn, 13)
                [{1:_}] /: res <- (nn, 41)
                [({1:_})] /: res <- (nn, 42)
                ([{1:_}]) /: res <- (nn, 43)
                
                [A{a1:11}, _] /: res <- (nn, 14)
                [A{a1:11}] /: res <- (nn, 141)
                (A{a1:11}) /: res <- (nn, 142)
                [(A{}, 11), (B{}, 22)] /: res <- (nn, 143)
                ([A{}, B{}], [B{}, C{}]) /: res <- (nn, 15)
                {'a':A{}, 'b':B{}} /: res <- (nn, 16)
                
                [*] /: res <- (nn, 917)
                (*) /: res <- (nn, 918)
                {*} /: res <- (nn, 919)
                _ /: res <- (nn, 999)
        
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
        null = Null()
        expv = [
            ('', 999), (null, 999), (0, 999), (False, 999), ((), 918), ({}, 919), ([], 917), 
            ([(), ()], 1), (([], []), 2), ([{}, {}], 3), (({}, {}), 4), ({1: [], 2: []}, 9), 
            ({1: (), 2: ()}, 10), ([{5: 5}, {}], 7), ([{5: 5}, {6: 7, 8: 9}], 7), 
            (({7: 7}, {}), 8), (({7: 7}, {8: 9, 11: 22}), 8), 
            ([{1: [(), ()], 2: [(), ()]}, {3: [(), ()], 4: [(), ()]}], 11), ([{1: ()}], 12), 
            (({1: []},), 13), ([{1: 22}], 41), ([({1: 33},)], 42), (([{1: [44]}],), 43), 
            (['st@A{a1: 11}'], 141), (['st@A{a1: 11}', 1], 14), ([('st@A{a1: 0}', 11), ('st@B{a1: 0,b1: 0}', 22)], 143),
            (('st@A{a1: 11}',), 142), ((['st@A{a1: 12}', 'st@B{a1: 0,b1: 13}'], ['st@B{a1: 0,b1: 14}', 'st@C{c1: 015}']), 15), 
            ({'a': 'st@A{a1: 0}', 'b': 'st@B{a1: 0,b1: 0}'}, 16), ({'a': 'st@A{a1: 22}', 'b': 'st@B{a1: 0,b1: 33}'}, 16)]
        self.assertEqual(expv, rvar.vals())

    def test_match_mixed_multicases(self):
        ''' replace(src, rx, repl) '''
        code = r'''
        res = []
        
        struct A a1:int
        struct B(A) b1: int
        struct C c1:string
        
        
        nns = [
            '', null, 0, false, (,), {}, [], 1, [2],
            [1,2,3], (1,2,3), {'a':1, 'b':2, 'c':3},
            A(1), B(0,2), C('c3'),
        ]
        for nn <- nns
            match nn
                false /: res <- (nn, -100)
                # 0 | null | false | "" | [] /: res <- (nn, 0)
                0 | null | "" | [] /: res <- (nn, 0)
                [1,2,3] | (1,2,3) | {'a':_, 'b':_, 'c':_} /: res <- (nn, 1)
                A{a1:1} | B{b1:2} | C{c1:'c3'} /: res <- (nn, 2)
                [*] | (*) | {*}  /: res <- (nn, 888)
                _ /: res <- (nn, 999)
        
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
        null = Null()
        expv = [
            ('', 0), (null, 0), (0, 0), (False, -100), ((), 888), ({}, 888), ([], 0), (1, 999), ([2], 888), 
            ([1, 2, 3], 1), ((1, 2, 3), 1), ({'a': 1, 'b': 2, 'c': 3}, 1), 
            ('st@A{a1: 1}', 2), ('st@B{a1: 0,b1: 2}', 2), ('st@C{c1: c3}', 2)]
        self.assertEqual(expv, rvar.vals())

    def test_match_simple_regexp(self):
        ''' pattern of struct, including collections in fields. '''
        code = r'''
        
        res = []
        nn = [
            'a', 'b', 'c', 'cc', 'd',
            'dd', 'def', 'fefefe', 'ddddddeeeee', 
            'naaa:111', 'nbbb:222', '333:cccc', 'def:445', 
            'houp', 'rupor', 'pirog', 'group', 'spore', 'hh',
            [], (,), {}, 1, 2.5, true, null
        ]
        
        for n <- nn
            match n
                re`a|b|c` /: res <- [n, 1] 
                re`[def]+$` /: res <- [n, 2] 
                re`([a-z]+\:[0-9]+)` /: res <- [n, 3] 
                re`^[houpring]{3,6}$` /: res <- [n, 4] 
                re`[0-9]+` /: res <- [n, 5] 
                re`.+` /: res <- [n, 999] 
                _ /: res <- [n, 2999]
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
        
        exp = [['a', 1], ['b', 1], ['c', 1], ['cc', 1], 
               ['d', 2], ['dd', 2], ['def', 2], ['fefefe', 2], ['ddddddeeeee', 2], 
               ['naaa:111', 3], ['nbbb:222', 3], ['333:cccc', 5], ['def:445', 3], 
               ['houp', 4], ['rupor', 4], ['pirog', 4], ['group', 4], 
               ['spore', 999], ['hh', 999], [[], 2999], [(), 2999], 
               [{}, 2999], [1, 2999], [2.5, 2999], [True, 2999], [Null(), 2999]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def test_match_any_struct(self):
        ''' pattern of struct, including collections in fields. '''
        code = r'''
        
        struct Type1 a:int, b:int
        struct TypeA color:string
        struct TypeB(TypeA) name:string, age:int
        struct TypeC color:int
        
        nn = [
            [], (,), {},
            Type1{},
            Type1(10, 20),
            TypeA('fff'),
            TypeB{color:'fff', name:'Aaa', age:44}, # child with `color`
            TypeC{}, TypeC(0xff0), # alternative case with `color`
            [Type1{}, TypeA{}], 
            [Type1(2,3), TypeA('red')], 
            {'tkey1': Type1(4,5)},
            {'tkey1': Type1(6,7), 'tkey2': TypeA('green')},
        ]
        res = []
        
        for n <- nn
            match n
                _{color:cval} /: res <- [n, (cval,), 10]
                _{} /: res <- [n, 19]
                [_{}, _{}] /: res <- [n, 20]
                {k1:_{}} /: res <- [n, k1, 21]
                {k1:_{}, k2:_{}} /: res <- [n, k1, k2, 22]
                {*} /: res <- [n, 28]
                _ /: res <- [n, 2999]
            # print('nres:', n)
        
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
            [[], 2999], [(), 2999], [{}, 28], ['st@Type1{a: 0,b: 0}', 19], ['st@Type1{a: 10,b: 20}', 19], 
            ['st@TypeA{color: fff}', ('fff',), 10], 
            ['st@TypeB{color: fff,name: Aaa,age: 44}', ('fff',), 10], 
            ['st@TypeC{color: 0}', (0,), 10], ['st@TypeC{color: 4080}', (4080,), 10],
            [['st@Type1{a: 0,b: 0}', 'st@TypeA{color: }'], 20],
            [['st@Type1{a: 2,b: 3}', 'st@TypeA{color: red}'], 20],
            [{'tkey1': 'st@Type1{a: 4,b: 5}'}, 'tkey1', 21], [{'tkey1': 'st@Type1{a: 6,b: 7}', 'tkey2': 'st@TypeA{color: green}'}, 'tkey1', 'tkey2', 22],
        ]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

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
                Type1{b:0} /: res <- [n, 10]
                Type1{a:10, b:20} /: res <- [n, 11]
                Type1{a:10} /: res <- [n, 12]
                Type1{} /: res <- [n, 19]
                TypeA{color:'fff'} /: res <- [n, 23]
                TypeB{name:name, age:22} /: res <- [n, (name), 21]
                TypeB{color:''} /: res <- [n, 27]
                TypeB{name:name, color:color} /: res <- [n, (name, color), 28]
                TypeA{color:_} /: res <- [n, 29]
                TypeC{nums:[]} /: res <- [n, 30]
                TypeC{nums:[331]} /: res <- [n, 31]
                TypeC{nums:[a, b, c]} /: res <- [n, (a,b,c), 32]
                TypeD{fd:{'a':aval,*}} /: res <- [n, (aval,), 41]
                TypeD{fl:[a, b, *]} /: res <- [n, (a,b), 42]
                TypeD{ft:(a), fd:{b:c}, fl:[d]} /: res <- [n, (a,b,c,d), 43]
                TypeD{ft:(a,*)} /: res <- [n, (a,), 44]
                TypeD{} /: res <- [n, 49]
                _ /: res <- [n, 2999]
            # print('nres:', res)
        # 
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        
        exp = [
            ['st@Type1{a: 0,b: 0}', 10], ['st@Type1{a: 10,b: 20}', 11], ['st@Type1{a: 10,b: 0}', 10], ['st@Type1{a: 10,b: 2}', 12], ['st@Type1{a: 1,b: 2}', 19], 
            ['st@TypeA{color: 000}', 29], ['st@TypeA{color: fff}', 23], ['st@TypeB{color: fff,name: Aaa,age: 44}', 23], 
            ['st@TypeB{color: red,name: Bimbo,age: 22}', 'Bimbo', 21], ['st@TypeB{color: ,name: ,age: 0}', 27], ['st@TypeB{color: green,name: Ambo,age: 33}', ('Ambo', 'green'), 28], 
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
            pattern :? guard /: ...
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
                101 :? 2 > 3 /: res <- [n, 'n0'] # should be skipped
                101 :? 2 < 3 /: res <- [n, 'n1']
                [a, b] :? a > b /: res <- [n, (a, b), 'n2']
                (a, _) | [_,a] :? a > 2 /: res <- [n, (a, ), 'n3']
                [*] | (*) :? 7 ?> n /: res <- [n, 'n7']
                {*} :? len(n) > 1 /: res <- [n, 'n52']
                {a:b} :? b > 8 /: res <- [n, (a, b), 'n51']
                1 |2 |3 :? n ?> [2, 3]  /: res <- [n, 'n61']
                (a, b, c) :? d = 16; c < d /: res <- [n, (a, b, c, d), 'n53']
                _  /: res <- [n, 999]
        
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
            [(1, 7, 5), 'n7'], [[1, 2, 1, 2, 1, 2, 7], 'n7'], 
            [{1: 11}, (1, 11), 'n51'], [{2: 22, 222: 222}, 'n52'], [{3: 33, 33: 333, 333: 3333}, 'n52'],
            [(1, 2, 3), (1, 2, 3, 16), 'n53'], [(11, 12, 15), (11, 12, 15, 16), 'n53']
        ]
        self.assertEqual(exp, rvar.vals())

    def test_multicase_simple(self):
        '''
        Multipattern as set of cases:
        each of sub case is valid
        match n
            1 | 2 | 3 /: ...
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
                1 /: res <- [n, 11]
                2 | 3 /: res <- [n, 22]
                4 | 5 | 6 /: res <- [n, 33]
                (_) | [_] | {_:_} /: res <- [n, 101]
                (a, *) | [a, *] | {a:_, _:_} /: res <- [n, (a,), 102]
                {*} | 4444 /: res <- [n, 103]
                _  /: res <- [n, 999]
        
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
                [*, 2]   /: res <- [n, 1021]
                (*, 2)   /: res <- [n, 21]
                (?, *, 41, ?, *, 42, ?, *)   /: res <- [n, 41]
                (a, _, ?,  9, *, b, c, 19, _, ?, *, d)   /: res <- [n, (a, b, c, d), 91]
                (a, _, ?,  9, *, b, c, 19, _, ?, *)   /: res <- [n, (a, b, c), 92]
                [*]      /: res <- [n, 1099]
                (*)      /: res <- [n, 99]
                _ /: res <- [n, 5999]
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
                [*, 2]   /: res <- [n, 21]
                [?, *, 3, *]   /: res <- [n, 31]
                [?, *, 41, ?, *, 42, ?, *]   /: res <- [n, 41]
                [_, 5, *]   /: res <- [n, 51]
                [*, _, 5]   /: res <- [n, 52]
                [5, *]   /: res <- [n, 53]
                [_, ?, 6, *, 61]   /: res <- [n, 61]
                
                [a, *, 7, *]   /: res <- [n,a, 71]
                [*, a, _, 8, b, *]   /: res <- [n, (a, b), 81]
                [a, _, ?,  9, *, b, c, 19, _, ?, *, d]   /: res <- [n, (a, b, c, d), 91]
                [a, _, ?,  9, *, b, c, 19, _, ?, *]   /: res <- [n, (a, b, c), 92]
                
                [*]      /: res <- [n, 99]
                _ /: res <- [n, 5999]
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
                (?, 2) /: res <- [n, 22]
                (?, 5,?) /: res <- [n, 53]
                (_, 5, ?) /: res <- [n, 54]
                (5, ?, ?) /: res <- [n, 55]
                (?) /: res <- [n, 11]
                (1, ?, 3) /: res <- [n, 31]
                (1, ?, ?, ?, 5) /: res <- [n, 51]
                (3,_,?) /: res <- [n, 32]
                (?, ?, ?, ?, a, 6) /: res <- [n, a, 61]
                (x, ?, ?, 4, ?, b, 7) /: res <- [n, (x,b), 71]
                (x, ?, ?, ?, a, b, 7) /: res <- [n, (x,a,b), 72]
                (x, ?, 7) /: res <- [n, (x), 73]
                _ /: res <- [n, 3999]
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
                [?, 2] /: res <- [n, 22]
                [?, 5,?] /: res <- [n, 53]
                [_, 5, ?] /: res <- [n, 54]
                [5, ?, ?] /: res <- [n, 55]
                [?] /: res <- [n, 11]
                [1, ?, 3] /: res <- [n, 31]
                [1, ?, ?, ?, 5] /: res <- [n, 51]
                [3,_,?] /: res <- [n, 32]
                [?, ?, ?, ?, a, 6] /: res <- [n, a, 61]
                [x, ?, ?, 4, ?, b, 7] /: res <- [n, (x,b), 71]
                [x, ?, ?, ?, a, b, 7] /: res <- [n, (x,a,b), 72]
                [x, ?, 7] /: res <- [n, (x), 73]
                _ /: res <- [n, 3999]
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
                {'a':_, ?} /: res <- [n, 12]
                {'b':v, ?} /: res <- [n, 13]
                {?} /: res <- [n, 11] # put here because it will eat empty and 1-pair cases
                {_:v, ?} /: res <- [n, 14] #  2-pairs and longer will reach here
                {'a':v, ?,?} /: res <- [n, 15] # a + possible 2
                {'b':v, ?,?, 'c':_} /: res <- [n, 16]
                {'a':v, ?,?,?,?} /: res <- [n, 17] # a + possible 4 elems
                {'a':v, *} /: res <- [n, 18] # a + more than 4 elems
                {'a':v, ?,?,?,?, *} /: res <- [n, 19] # the same as prev
                {*} /: res <- [n, 20]
                _ /: res <- [n, 3999]
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
                {'a':v} /: res <- [n, 12]
                {'a':v1, 'b': v2, *} /: res <- [n, 21]
                {'a':v1, 'c': v2, *} /: res <- [n, 22]
                {'a':v, *} /: res <- [n, 23]
                {k:v, _:_, _:_, *} /: res <- [n, 24]
                {k:v} /: res <- [n, 25]
                {k:'_n1', *} /: res <- [n, 26]
                {*} /: res <- [n, 30]
                _ /: res <- [n, 3999]
        
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
                {'bb':v} /: res <- [n, v, 18]
                {k:'33'} /: res <- [n, 19]
                {k:v} /: res <- [n, (k,v), 21]
                {'aa':v1, 'bb':v2} /: res <- [n, (v1, v2), 22]
                {'aa':v1, _:v2} /: res <- [n, 23]
                {_:v1, 'ee':v2} /: res <- [n, (v1,v2), 25]
                {'77': val, _:_} /: res <- [n, 27]
                {a:b, c:d} /: res <- [n, 28]
                {'a1':v1, 'a2':v2, _:v3} /: res <- [n, 31]
                {'b2':v2, 'b3':v3, _:v1} /: res <- [n, 32]
                {'c3':v3, k2:'222', k1:v1} /: res <- [n, 33]
                {a:'__1', b:c, _:_} /: res <- [n, 335] # doubtful case, value of key in dict is not unique
                {a:b, c:d, e:f} /: res <- [n, 36]
                _ /: res <- [n, 2999]
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
                {0:_} /: res <- [n, 19]
                {'':_} /: res <- [n, 20]
                {' ':_} /: res <- [n, 21]
                {'_':v} /: res <- [n, (v,), 22]
                {k:v} /: res <- [n, (k,v), 23]
                {null:v, _:_} /: res <- [n, 25]
                {'':v, _:_} /: res <- [n, 26]
                _ /: res <- [n, 2999]
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
                () /: res <- [n, 11]
                [] /: res <-   [n, 12]
                {} /: res <- [n, 13]
                {1:_} /: res <- [n, 16] # num key
                {'aa':_} /: res <- [n, 17] # str key
                {k:'33'} /: res <- [n, 19] # key va and str val
                {_:_} /: res <- [n, 21] # any : any
                {'aa':v1, _:_} /: res <- [n, 23] # 2 pairs
                {'a1':v1, 'a2':v2, _:v3} /: res <- [n, 31] # 3 pairs, 2 key vals
                _ /: res <- [n, 2999]
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
                () /: res <- [n, 11]
                (2) /: res <- [n, 11]
                (a) /: res <-   [n, (a,), 12]
                (_) /: res <- [n, 19] # shouldn't be used because prev
                (a,2) /: res <- [n, (a,), 13]
                (a,b) /: res <- [n, (a,b), 14]
                (a,_,3) /: res <- [n, (a,), 21]
                (a,b,22) /: res <- [n, (a,b), 222]
                (a,b,c) /: res <- [n, (a,b,c), 26]
                _ /: res <- [n, 2999]
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
                [] /: res <- [n, 11]
                [a] /: res <-   [n, (a,), 12]
                [_] /: res <- [n, 19] # shouldn't be used because prev
                [a,2] /: res <- [n, (a,), 13]
                [a,b] /: res <- [n, (a,b), 14]
                [a,_,1] /: res <- [n, (a,), 23]
                [a,_,3] /: res <- [n, (a,), 23]
                [a,b,22] /: res <- [n, (a,b), 23]
                [a,b,c] /: res <- [n, (a,b,c), 26]
                _ /: res <- [n, 2999]
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
                # 1 /: 1
                () /: res <- [n, 101]
                (1) /: res <-   [n, 102]
                (1,7) /: res <- [n, 103]
                (_) /: res <- [n, 201]
                (1,_) /: res <- [n, 202]
                (_,2) /: res <- [n, 203]
                (_,_) /: res <- [n, 204]
                (1,_,7) /: res <- [n, 205]
                (_,_,_) /: res <- [n, 206]
                _ /: res <- [n, 20999]

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
                [] /: res <- [n, 11]
                ['1'] /: res <-   [n, 12]
                ['a'] /: res <- [n, 13]
                ['bb'] /: res <- [n, 14]
                ['','',''] /: res <- [n, 15]
                ['a','bb'] /: res <- [n, 16]
                ['aa','cc'] /: res <- [n, 17]
                ['aaa','_'] /: res <- [n, 18]
                ['a',_] /: res <- [n, 19]
                [a, b] /: res <- [n, (a,b), 20]
                [_] /: res <- [n, 21]
                _ /: res <- [n, 2999]
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
                # 1 /: 1
                [] /: res <- [n, 11]
                [1] /: res <-   [n, 12]
                [1,7] /: res <- [n, 13]
                [_] /: res <- [n, 21]
                [1,_] /: res <- [n, 22]
                [_,2] /: res <- [n, 23]
                [_,_] /: res <- [n, 24]
                [1,_,7] /: res <- [n, 25]
                [_,_,_] /: res <- [n, 26]
                _ /: res <- [n, 2999]
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
                '' /:      res <- [s, 1]
                ' ' /:      res <- [s, 2]
                'aaa' /:   res <- [s, 3]
                'b' /:     res <- [s, 4]
                'bcd' /:   res <- [s, 5]
                '123' /:   res <- [s, 123]
                _ /:
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
                1 /: res <- [n,111]
                2 /: res <- [n,222]
                _ /: res <- [n,999]
        
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
            1  /: r1 = 100
            10 /: r1 = 200
            b  /: r1 = 300
            _  /: r1 = -2
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
                1 /: res = 10
                2
                    if res > 0 && res < 4
                        # print('c2', i, res)
                        res *= 11 * i
                3 /: res = foo2(x -> x ** 2)
                4 /: f = x -> x * 12
                    res = f(i)
                5 /: res = foo2(ff) + i
                6 
                    for j <- [0..5]
                        # print('c5', j, res)
                        res += i
                # unnecessary operator /: before explicit block by indent
                7 /:
                    for j = 1; j < 6; j = j + 1
                        # print('c7', j, res)
                        res *= j
                8
                    if c= t + 100; c > 110 && t > 4
                        # print('c2', i, res)
                        res = c
                _ /: res = 1001
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


    # deprecated by refactoring of match cases
    # def _test_CaseMatchSub_match(self):
    #     cs = CaseMatchCase()
    #     rrs = []
    #     def checkRes(code, exp):
    #         dprint('$$ run test ------------------')
    #         dprint('CODE:','\n'+code)
    #         # code = lines[0]
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         res = cs.match(elems)
    #         dprint('#tt >>> ', code, res)
    #         msg = 'Tried use code: %s' % code
    #         if exp:
    #             self.assertTrue(res, msg)
    #         else:
    #             self.assertFalse(res, msg)
            
    #     src = ''''
    #     val /: expr
    #     123 /: a + b
    #     234 /: r = 2 + 3
    #     3 /: res = 4
    #     user(123) /: res
    #     '''
    #     src = norm(src[1:].rstrip())
    #     data = src.splitlines()
    #     for code in data:
    #         if code.strip() == '':
    #             continue
    #         checkRes(code, True)
        
    #     src = ''''
    #     val 123 -> expr
    #     1,2,3 -> a + b
    #     x <- src
    #     -> expr ...
    #     user(123) + 0 -> res
    #     '''
    #     src = norm(src[1:].rstrip())
    #     data = src.splitlines()
    #     for code in data:
    #         if code.strip() == '':
    #             continue
    #         checkRes(code, False)


if __name__ == '__main__':
    main()
