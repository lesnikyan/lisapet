
from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from cases.utils import *
from context import Context
from nodes.tnodes import Var
from nodes.structs import *
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from tree import *
from eval import rootContext

from tests.utils import *


class TestOper(TestCase):



    def test_type_operator_for_struct(self):
        ''' var :: StructType|StructType|list '''
        code = r'''
        res = []
        
        struct A
        struct B
        struct C(B) x:int # empty inherited still need to be fixed
        struct D
        
        # simple type check
        a1 = A{}
        res <- ('A::A', a1 :: A)
        res <- ('A::B', a1 :: B)
        
        b1 = B{}
        res <- ('B::B', b1 :: B)
        res <- ('B::A', b1 :: A)
        
        c1 = C{}
        res <- ('C::C', c1 :: C)
        res <- ('C::A', c1 :: A)
        res <- ('C::B', c1 :: B)
        
        res <- 'AB'
        ab: A|B = null
        res <- ab
        ab = A{}
        res <- ('ab :: A|D', ab, ab :: A|D)
        ab = B{}
        res <- ('ab :: A|D', ab, ab :: A|D)
        
        res <- ('C :: A|D', c1, c1 :: A|D)
        res <- ('C :: A|B', c1, c1 :: A|B)
        
        # res = []
        d1 = D{}
        t1 = A|C
        res <- ('A :: var(A|C)', a1, a1 :: t1)
        res <- ('C :: var(A|C)', c1, c1 :: t1)
        res <- ('B :: var(A|C)', b1, b1 :: t1)
        res <- ('D :: var(A|C)', d1, d1 :: t1)
        
        tab = A|B
        res <- ('C :: var(A|B)', c1, c1 :: tab) # inherited
        res <- ('D :: var(A|B)', d1, d1 :: tab)
        
        
        if a1 :: (A|B)
            res <- 'if/1'
            
        if a1 :: (D|B) # no
            res <- 'if/2'
        
        if d1 :: (A|D)
            res <- 'if/3'
        
        # mixed 
        if a1 :: A|int
            res <- 'if/4'
        
        if 5 :: A|int
            res <- 'if/5'
        
        nn = [1,2,3]
        if nn :: A|list
            res <- 'if/6'
        
        ff = x -> x + 2
        
        if ff :: A|function
            res <- 'if/7'
            
        if a1 :: A|function
            res <- 'if/8'
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        null = Null()
        exv = [
            ('A::A', True), ('A::B', False), ('B::B', True), ('B::A', False), ('C::C', True), ('C::A', False), ('C::B', True), 
            'AB', null, ('ab :: A|D', 'st@A{}', True), ('ab :: A|D', 'st@B{}', False), 
            ('C :: A|D', 'st@C{x: 0}', False), ('C :: A|B', 'st@C{x: 0}', True), 
            ('A :: var(A|C)', 'st@A{}', True), ('C :: var(A|C)', 'st@C{x: 0}', True), ('B :: var(A|C)', 'st@B{}', False), 
            ('D :: var(A|C)', 'st@D{}', False), ('C :: var(A|B)', 'st@C{x: 0}', True), ('D :: var(A|B)', 'st@D{}', False), 
            'if/1', 'if/3', 'if/4', 'if/5', 'if/6', 'if/7', 'if/8']
        self.assertEqual(exv, rvar.vals())

    def test_multitype_type_operator(self):
        ''' '''
        code = r'''
        res = []
        
        x = 2
        if x :: int|float
            res <- '2 :: int|float'
        
        x = 2.5
        if x :: int|float
            res <- '2.5 :: int|float'
        
        typeVal = int|bool
        x = true
        if x :: typeVal
            res <- 'true :: var(int|bool)'
        
        x = 33
        if x :: typeVal
            res <- '33 :: var(int|bool)'
        
        
        y = 1
        z = 1.2
        res <- 'y :: int || z :: float'
        nn = {-1:1.2, 1.1: 1.1,  1.2: 2, true:[], 3:[3], 4:'aaa'}
        for y, z <- nn
            if y :: int || z :: float
                res <- (y,z)
        
        res <- 'y :: int|bool && z :: float|string'
        for y, z <- nn
            if y :: int|bool && z :: float|string
                res <- (y,z)
        
        res <- 'while x :: list'
        x = [1,2,3,4,5]
        while x :: list
            last = x - [-1]
            # print(x)
            if len(x) == 0
                x = 0
            res <- (last, x)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '2 :: int|float', '2.5 :: int|float', 'true :: var(int|bool)', '33 :: var(int|bool)', 
            'y :: int || z :: float', (-1, 1.2), (1.1, 1.1), (True, []), (3, [3]), (4, 'aaa'), 
            'y :: int|bool && z :: float|string', (-1, 1.2), (4, 'aaa'), 
            'while x :: list', (5, []), (4, []), (3, []), (2, []), (1, 0)]
        self.assertEqual(exv, rvar.vals())

    def test_code_get_string_elem(self):
        ''' test str[index] '''
        code = (r'''
        res = [11]
        s1 = 'abcd1'
        s2 = "efgh2"
        s3 = `ijk3`
        '''
        """
        s4 = '''mnop4'''
        """
        r'''
        s5 = """qrst"""
        s6 = ```uvwxyz```
        nums = '0123456789'
        
        struct A a:string
        struct B(A) b: string
        
        aa= A('qwerty')
        bb = B{a:'perin', b:'xyzlog'}
        sss = ['abc', 'def']
        
        func foo()
            "function_resUlT"
        
        src = [
            ("abc", 0),
            ('def', 2),
            (`hijk`, -1),
            (s1, 0),
            (s1, 3),
            (s2, 1),
            (s2, -1),
            (s3, 1),
            (s3, 2),
            (s4, 0),
            (s4, 1),
            (s5, 0),
            (s5, 2),
            (s6, 1),
            (s6, -1),
            (nums, 0),
            (nums, 5),
            (aa.a, 2),
            (bb.a, -1),
            (bb.b, 2),
            (sss[0], 1),
            (sss[1], 2),
            (foo(), 2),
            (foo(), 8),
            (foo(), -3),
            (foo() + `</~:>`, -3),
            
        ]
        
        for t <- src
            s, index = t
            res <- (s, index, s[index]) 
        
        
        # print('res = ', res)
        ''')
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exv = [11, 
               ('abc', 0, 'a'), ('def', 2, 'f'), ('hijk', -1, 'k'), ('abcd1', 0, 'a'), ('abcd1', 3, 'd'), 
               ('efgh2', 1, 'f'), ('efgh2', -1, '2'), ('ijk3', 1, 'j'), ('ijk3', 2, 'k'), 
               ('mnop4', 0, 'm'), ('mnop4', 1, 'n'), ('qrst', 0, 'q'), ('qrst', 2, 's'), 
               ('uvwxyz', 1, 'v'), ('uvwxyz', -1, 'z'), ('0123456789', 0, '0'), ('0123456789', 5, '5'), 
               ('qwerty', 2, 'e'), ('perin', -1, 'n'), ('xyzlog', 2, 'z'), ('abc', 1, 'b'), ('def', 2, 'f'), 
               ('function_resUlT', 2, 'n'), ('function_resUlT', 8, '_'), 
               ('function_resUlT', -3, 'U'), ('function_resUlT</~:>', -3, '~')]
        self.assertEqual(exv, rvar.vals())

    def test_code_string_plus(self):
        ''' test str + str '''
        code = (r'''
        res = [11]
        s1 = 'abcd1'
        s2 = "efgh2"
        s3 = `ijk3`
        '''
        """
        s4 = '''mnop4'''
        """
        r'''
        s5 = """qrst"""
        s6 = ```uvwxyz```
        nums = '0123456789'
        
        struct A a:string
        struct B(A) b: string
        
        aa= A('qwerty')
        bb = B{a:'perin', b:'xyzlog'}
        sss = ['abc', 'def']
        
        func foo()
            "function_resUlT"
        
        res = [
            "" + "", '' + '', `` + ``,
            "a" + `b`,
            'c' + "def",
            """mult1_""" + ```-mult2```,
            s1 + s2,
            foo() + s3,
            s4 + "!~/",
            """ 
            mult3
            arba jambo,
            """ + s5, nums + s6, 
            aa.a + "Aa-",
            `B:` + bb.b + "" + bb.a, 
            "sss:" + sss[0] + sss[1] 
        ]
        
        # print('res = ', res)
        ''')
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exv = ['', '', '', 'ab', 'cdef', 'mult1_-mult2', 'abcd1efgh2', 'function_resUlTijk3', 
               'mnop4!~/', ' \n    mult3\n    arba jambo,\n    qrst', '0123456789uvwxyz', 
               'qwertyAa-', 'B:xyzlogperin', 'sss:abcdef']
        self.assertEqual(exv, rvar.vals())

    def test_type_check_operator(self):
        ''' replace(src, rx, repl) '''
        code = r'''
        res = []
        x:float = 1.5555
        
        res <- (1, 'int', (1 :: int))
        res <- (-1, 'int', 1 :: int)
        res <- (1000000, 'int', 1 :: int)
        res <- (0xffff, 'int', 1 :: int)
        res <- (1., 'int', 1. :: int)
        res <- (1., 'float', 1. :: float)
        res <- (x, 'int', x :: int)
        res <- (x, 'float', x :: float)
        typeL = list # type in var
        res <- ([], 'list', [] :: typeL)
        res <- ("list", 'list', "list" :: list)
        res <- ((1,), 'tuple', (1,) :: tuple)
        res <- ({1:2}, 'dict', {1:2} :: dict)
        res <- ({}, 'dict', {} :: dict)
        res <- (true, 'bool', true :: bool)
        res <- (false, 'bool', false :: bool)
        res <- ("abc", 'string', "abc" :: string)
        f1 = x -> x * 2
        res <- ('x -> x * 2', 'function', f1 :: int)
        res <- ('x -> x * 2', 'function', f1 :: function)
        
        # print('res', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        # ctx.print(forsed=1)
        ex.do(ctx)
        rvar = ctx.get('res').get()

        # null = Null()
        expv = [
            (1, 'int', True), (-1, 'int', True), (1000000, 'int', True), (65535, 'int', True),
            (1.0, 'int', False), (1.0, 'float', True), (1.5555, 'int', False), 
            (1.5555, 'float', True), ([], 'list', True), ('list', 'list', False), ((1,), 'tuple', True), 
            ({1: 2}, 'dict', True), ({}, 'dict', True), (True, 'bool', True), (False, 'bool', True), 
            ('abc', 'string', True), ('x -> x * 2', 'function', False), ('x -> x * 2', 'function', True)]
        self.assertEqual(expv, rvar.vals())

    def test_brackets_after_brackets(self):
        ''' slice of generator: 
                iter gen [a..n][a..b], 
                sequence gen: [x ; x <- src][a..b]
                foo()[a..b]
            func obj in brakets: (function)(), (lambda)() 
            func ojb in collection: funcs[key]()
            func returns func: foo()()
            
            '''
        code = r'''
        res = []
        r1 = (x -> x + 10)(2)
        res <- r1
        
        f2 = x -> x + 100
        ff = [f2]
        r2 = ff[0](3)
        res <- r2
        
        r3 = [1..5][0:3]
        res <- r3
        
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
        self.assertEqual([12, 103, [1, 2, 3]], rvar.vals())

    def test_not_in_list(self):
        ''' '''
        code = r'''
        res = 0
        dt = [0, 5, 11] # data
        tst = [0, 1, 2, 5, 10, 11, 100] # test vals
        res = []
        for v <- tst
            r1 = v ?> dt # have
            r2 = v !?> dt # don't have
            res <- [v, r1, r2]
        dd = {'a':'123', 'b':'345'}
        tsd = ['a','bb','c']
        for v <- tsd
            r1 = v ?> dd # have
            r2 = v !?> dd # don't have
            res <- [v, r1, r2]
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [
            [0, True, False],
            [1, False, True],
            [2, False, True],
            [5, True, False],
            [10, False, True],
            [11, True, False],
            [100, False, True],
            ['a', True, False],
            ['bb', False, True],
            ['c', False, True],
        ]
        self.assertEqual(exp, rvar.vals())

    def test_semicolon_diff_as_1_line_block(self):
        ''' expr1; expr2; expr3 
        sequence of expressions in one line'''
        code = r'''
        
        func sum(nums)
            r = 0
            for n <- nums
                r += n
            r
        
        func bar(x, y)
            r = 1; p = 0
            r *= sum(x); p += sum(y); (r, p)
        
        a = 1; b = 2; c = 3
        a = 10 + a; b += 20; c -= 30;
        nn = [1,2,3,4,5]; dd = sum(nn)
        e = 0; _ = [n; n <- [4..8]; e += n]
        
        res = [a, b, c]; res <- dd; res <- e
        g = [3..5]; h = [3..7]; vv = bar(g, h); k, m = vv; res <- k; res <- m
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [11, 22, -27, 15, 30, 12, 25]
        self.assertEqual(exp, rvar.vals())

    def test_in_coll_oper(self):
        ''' val ?> list|dict|tuple 
        true == 1, false == 0
        '''
        code = r'''
        
        src1 = [1, 2, 3]
        src2 = {'a':1, 'b':2,'c':3}
        src3 = (11,0,3)
        src4 = ['a', 'b', 'c']
        src5 = 'lorem ipsum dolor'
        
        res = []
        
        res <- 1 ?> src1
        res <- 10 ?> src1
        res <- 'a' ?> src2
        res <- 'z' ?> src2
        res <- 3 ?> src3
        res <- -3 ?> src3
        res <- 'b' ?> src4
        res <- 0 ?> src4
        
        res <- true ?> src1
        res <- true ?> src2
        res <- true ?> src3
        res <- true ?> src4
        res <- false ?> src1
        res <- false ?> src2
        res <- false ?> src3
        res <- false ?> src4
        
        res <- 1 ?> [1,2,3]
        res <- 10 ?> [1,2,3]
        res <- 2 ?> (2,3,4)
        res <- 1 ?> (2,3,4)
        
        res <- 'a' ?> src5
        res <- 'sum' ?> src5
        res <- 'a' ?> "lorem ipsum dolor"
        res <- 'sum' ?> 'lorem ipsum dolor'
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [True, False, True, False, True, False, True, False, 
               True, False, False, False, False, False, True, False,
               True, False, True, False,
               False, True, False, True]
        # dprint(rvar.vals())
        self.assertEqual(exp, rvar.vals())

    def test_false_or_oper(self):
        ''' a ?: b '''
        code = r'''
        res = []
        a = false
        b = null
        c = []
        d = 0
        
        func foo(x)
            x - 5
        
        struct A a1:int
        
        sa1:A = A{a1:10}
        sa2:A = null
        
        res <-  false ?: true
        res <-  a ?: true
        res <-  true ?: false
        res <-  true ?: true
        res <-  false ?: false
        res <-  foo(5) ?: foo(7)
        res <-  foo(7) ?: foo(5)
        res <-  c ?: [1,2,3]
        res <-  c ?: []
        
        
        r1 = sa2 ?: sa1
        r2 = sa1 ?: sa2
        
        # print('res = ', res, '##', r1, r2)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [True, True, True, True, False, 2, 2, [1,2,3], []]
        self.assertEqual(exp, rvar.vals())
        
        r1 = ctx.get('r1').get()
        self.assertIsInstance(r1.getType(), TypeStruct)
        r2 = ctx.get('r2').get()
        self.assertIsInstance(r2.getType(), TypeStruct)

    def test_ternar_oper(self):
        ''' '''
        code = r'''
        res = 0
        a = 3
        b = 5
        c = 4
        
        res = a < b ? 2 : 1 + 2 # 2
        res += (b % a < 3 ? 1 : 1 + 1 ) # 3
        res += a - b >= 1 ? 5 : c # 7 
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(7, rvar.getVal())


    def test_find_main_operator(self):
        '''find position of main operator in string
            main opertaor is an operator which will split line to 2 operands.
            if result == 0 it means that it unary or opening brackets.
        '''
        code = '''
        12 + 5 - 7 * 9 # 3
        2 * 3 - 4 * -5 ** 2 + 6 ** 3 * 7 # 10
        a = 5 * 2 # 1
        b = qq || ww # 1
        (1,2,3) + [4,5,6] # 7
        a + b ?: d - 111 # 3
        [1,2,3] * 2 ** 2 # 7
        foo(x, y.abc) > 5 && len(bar([..100], 7)) < 5 * z # 10
        a, b <- c # 3
        'aa' : 11, 'bb' : 22, cc : 33, dd(arg, arg) : 44 # 11
        a, b, c = f1(), f2(), {a:1, b:2} # 5
        foo().memb[bar(5)] # 3
        x + 2 ; x <- [3 .. 9] ; x % 2 == 0 # 11
        foo() # -1
        bar # -1
        - 1000 # 0
        ! (true && foo()) # 0
        - 2 * (abc - 7) # 0
        1 + 2 , 3 # 3
        1 , 2 # 1
        ( 1, 2, 3 ) # 0
        [(0), [111], {22:222}] # 0
        [1 .. 2] # 0
        [a + 2 : -1] # 0
        [x + 2 ; x <- [5 .. 10] ; x % 2 > 0] # 0
        {'aa' : 11, 'bb' : 22, cc : 33, dd(arg, arg) : 44} # 0
        
        '''
        code = norm(code[1:])
        src = code.splitlines()
        spl = OperSplitter()
        for sline in src:
            if len(sline) == 0:
                continue
            tsrc, exp = sline.split('#')
            exp = int(exp.strip())
            tlines = splitLexems(tsrc)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            pos = spl.mainOper(elems)
            self.assertEqual(exp, pos, 'in line: %s' % sline)

    def test_colon_vs_other(self):
        ''' test priority of colon operator  '''
        code = '''
        d1 = {'a': 10 + 1}
        struct T1 bb:int
        t1 = T1{bb:4}
        d2 = {'b': 20 / t1.bb}
        
        # print(d1['a'], d2['b'])
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_last_sqr_brackets(self):
        data = [
            ('arr[1]', 1),
            ('arr[x[123]]', 1),
            ('arr[foo()]', 1),
            ('arr[1][2]', 4),
            ('arr[1:2]', 1),
            ('arr[1][1:2]', 4),
            ('arr[1:2][2]', 6),
            ('arr[1][2][3]', 7),
            ('foo(arg)[1]', 4),
            ('foo({a:1, a:2})[1][2]', 15),
        ]
        for tt in data:
            code = tt[0]
            exp = tt[1]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            opInd = findLastBrackets(elems)
            self.assertEqual(exp, opInd, 'Error in code `%s`' % code)

    def test_bool_unary(self):
        ''' test inversion bool. '''
        code = r'''
        func unar(cond)
            inv = false
            if cond && ! inv
                return true
            false

        res = unar(true)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        self.assertEqual(True, ctx.get('res').getVal())

    def test_CaseBinAssign(self):
        init = '''
        x = 200
        varr = 2*3*5*7*100
        barr = 2*3*5*7*100
        arr = [0,1,2,32,4,5]
        data = [10,20,30,40,50]
        key = 2
        a = 1
        b = 2
        '''
        srcT = '''
        x *= 35; res = x
        varr += 1; res = varr
        arr[2] += 2; res = arr[2]
        arr[a + b] += 3; res = arr[a + b]
        data[key] += 4; res = data[key]
        varr -= 6; res = varr
        varr /= 7; res = varr
        arr[3] %= 11; res = arr[3]
        '''
        init = norm(init[1:]).splitlines()
        src = norm(srcT[1:])
        data = src.splitlines()
        rrs = []
        for code in data:
            # dprint('$$ run test ------------------')
            lines = code.split('; ')
            code = '\n'.join(init+lines)
            # dprint('CODE:','\n\n'+code)
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            # dprint('$$ eval expr ------------------')
            exp.do(ctx)
            res = ctx.get('res').get()
            barr = ctx.get('barr').get()
            rrs.append((res, barr,))
        # dprint('# tt>> ', rrs)


    def test_operators_order(self):
        '() [] . , -x !x ~x , ** , * / % , + - , << >> , < <= > >= -> !>, == != , &, ^ , | , && , ||, = += -= *= /= %=  '
        s = 'a = 5 + 6 - 7*(b - c * 10 - 5) / 11 + 3 ** d - 0xe * 5'
        s = 'a = 5 + (2 - 1) * (3 - 4)/ (-1)'
        s = 'a = 5 + sum([1,2,3, b, c + 3])' # TODO: functios
        cs = CaseBinOper()
        for gr in cs.priorGroups:
            # dprint(gr)
            pass
        matchCases = [
            'x - 2',
            '2 + x - 5',
            'name == "Vasya"',
            '8 << 2',
        ]
        for mc in  matchCases:
            tlines = splitLexems(mc)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # print('#t1 mr:', mc, mres)
    
    def test_CaseUnar_split(self):
        data = [
            ('- 5', -5), 
            ('-0xa0013bc', -0xa0013bc), 
            ('!ddd', False),  
            ('~0x0abc', -2749), 
            ('-123456789', -123456789), 
            ('-(-(-num1))', 17), 
            ('-(-(-(-(-(-111)))))', 111), 
            ('!(!(!(!(!((!true))))))', True)
        ]
        ctxData = {'ddd':True, 'num1':-17}
        cs = CaseUnar()
        for tcase in  data:
            td, exv = tcase
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # print('mres', mres)
            self.assertTrue(mres)
            ctx = rootContext()
            def tvar(k, v):
                vv = Var(k, TypeAny)
                vv.set(Val(v, TypeAny))
                return vv
            ctx.addSet({k: tvar(k, v) for k,v in ctxData.items()})
            ex = elems2expr(elems)
            # print('#tc11', td, mres)
            ex.do(ctx)
            res = ex.get()
            self.assertEqual(exv, res.get())
            # print(' -- #tr11',td, res.getType(), res.get())
    
    def test_CaseUnar(self):
        data = ['- 5', '-0xa0013bc', '!foo(1,2,ddd)', '!foo(bar(1,2,3, baz("aa a aa")))', '~0xabcdef0011', 
                '~ foo(agr1, arg2)', '-(foo(2-5)+bar(7-num4))']
        
        cs = CaseUnar()
        for td in  data:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # print('#tc11', td, mres)
            self.assertTrue(mres)
        
        # dprint('##test_CaseUnar False')
        # match false
        fdata = ['-5 + num1', '-(2+3)-a*b-c', '! val && true', '~ num ^ 0x0011']
        cs = CaseUnar()
        for td in  fdata:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # print('#tc12', td, mres)
            self.assertFalse(mres)
    
    def test_CaseBinOper_split(self):
        ''' '''
        data = [
            ('1+2-3 * 4 + 5', {}, -4),
            ('5 + 6 - 7*(b - c * 12 - 15) / 10 + 3 ** d - 0xe * 8', {'b':100, 'c':4, 'd':3}, -99.9),
            ('5 + (2 - 1) * (3 - 4)/ (1)',{}, 4.0),
            ('5 + sum([1,2,3, b, c + 31])', {'b':10, 'c':20}, 72)
        ]
        fcode = '''
        func sum(nums)
            nums.fold(0, (p, c) -> c + p)
        '''
        fcode = norm(fcode[1:])
        fex = tryParse(fcode)
        for mc in  data:
            tcode, vars, exv = mc
            rCtx = rootContext()
            ctx = rCtx.moduleContext()
            trydo(fex, ctx)
            
            tlines = splitLexems(tcode)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            ex = elems2expr(elems)
            
            def tvar(k, v):
                vv = Var(k, TypeInt())
                vv.set(Val(v, TypeInt()))
                return vv
            
            ctx.addSet({k: tvar(k, v) for k, v in vars.items()})
            trydo(ex, ctx)
            res = ex.get().getVal()
            self.assertEqual(exv, res)

    def test_line_assign(self):
        data = [
            ('x = 5.0', 5.0, TypeFloat),
            ('x = 5j2', (5+2j), TypeComplex),
            ('x = 0xf000a', 0xf000a, TypeInt),
            ("x = '5' ", '5', TypeString),
            ('x = 0b10101', 21, TypeInt),
            ('x = [5]', [5], TypeList),
            ('x = q -> q + 1', 'func @lambda(q)', TypeFunc),
        ]
        for tcase in data:
            src, exv, extype = tcase
            tlines = splitLexems(src)
            clines = elemStream(tlines)
            line0 = clines[0]
            expr = line2expr(line0)
            ctx = Context(None)
            expr.do(ctx)
            rval = ctx.get('x')
            res = rval
            if not isinstance(res.val, Function):
                res = rval.get()
            # results.append(rval.getVal())
            # print('#a7 ===> ', res.get(), res.getType())
            self.assertIsInstance(res.getType(), extype)
            val = res.get()
            if isinstance(val, Function):
                val = str(val)
            self.assertEqual(exv, val)


if __name__ == '__main__':
    main()
