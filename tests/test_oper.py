
from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
# from objects.func import Function
# from nodes.func_expr import setNativeFunc
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext

from tests.utils import *

import pdb


class TestOper(TestCase):


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
        
        # res <- '12'
        
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
        
        
        print('res = ', res)
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
        res <- ([], 'list', [] :: list)
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
            TODO: function in expr with brackets:
            func obj in brakets: (function)(), (lambda)() 
            func ojb in collection: funcs[key]()
            func returns func: foo()()
            
            '''
        code = r'''
        res = 0
        r1 = (x -> x + 10)(2)
        
        f2 = x -> x + 100
        ff = [f2]
        # r2 = ff[0](3)
        
        r3 = [1..5][0:3]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        # rCtx = rootContext()
        # ctx = rCtx.moduleContext()
        # ex.do(ctx)
        # rvar = ctx.get('res')
        # self.assertEqual(0, rvar.getVal())

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
        # SequenceExpr, CaseSemic

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
            # dprint(exp, sline)
            # continue
            tlines = splitLexems(tsrc)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            pos = spl.mainOper(elems)
            # dprint('tt `%s`' % sline, ' >>> ', pos)
            self.assertEqual(exp, pos, 'in line: %s' % sline)

    def test_colon_vs_other(self):
        ''' make vars and assign vals from tuple  '''
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
            # dprint('#t1 mr:', mc, mres)
    
    def test_CaseUnar_split(self):
        data = ['- 5', '-0xa0013bc', '!ddd',  '~0x0abc', '-123456789', '-(-(-num1))', '-(-(-(-(-(-111)))))', '!(!(!(!(!((!true))))))']
        ctxData = {'ddd':True, 'num1':-17}
        cs = CaseUnar()
        for td in  data:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            ctx = rootContext()
            def tvar(k, v):
                vv = Var(k, TypeAny)
                vv.set(Val(v, TypeAny))
                return vv
            ctx.addSet({k: tvar(k, v) for k,v in ctxData.items()})
            # dprint('#tc11', td, mres)
            ex = elems2expr(elems)
            ex.do(ctx)
            res = ex.get()
            # dprint(' -- #tr11',td, res.getType(), res.get())
    
    def test_CaseUnar(self):
        
        # dprint('##test_CaseUnar True')
        # match true
        data = ['- 5', '-0xa0013bc', '!foo(1,2,ddd)', '!foo(bar(1,2,3, baz("aa a aa")))', '~0xabcdef0011', 
                '~ foo(agr1, arg2)', '-(foo(2-5)+bar(7-num4))']
        
        cs = CaseUnar()
        for td in  data:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # dprint('#tc11', td, mres)
        
        # dprint('##test_CaseUnar False')
        # match false
        fdata = ['-5 + num1', '-(2+3)-a*b-c', '! val && true', '~ num ^ 0x0011']
        cs = CaseUnar()
        for td in  fdata:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            # dprint('#tc12', td, mres)
    
    def test_CaseBinOper_split(self):
        ''' '''
        data = [
            ('1+2-3 * 4 + 5', {}),
            ('5 + 6 - 7*(b - c * 12 - 15) / 11 + 3 ** d - 0xe * 8', {'b':100, 'c':4, 'd':3}), # -97.54545454545455
            ('5 + (2 - 1) * (3 - 4)/ (1)',{}),
            # ('5 + sum([1,2,3, b, c + 3])', {})
        ]
        cs = CaseBinOper()
        for mc in  data:
            tlines = splitLexems(mc[0])
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            ex = elems2expr(elems)
            ctx = Context(None)
            
            def tvar(k, v):
                # print('## tvar:', k, v)
                vv = Var(k, TypeInt())
                vv.set(Val(v, TypeInt()))
                return vv
            
            ctx.addSet({k: tvar(k, v) for k, v in mc[1].items()})
            # ctx.print()
            ex.do(ctx)
        

    def test_line_assign(self):
        data = [
            'x = 5.0', 'x = 5j2', 'x = 0xf000a', "x = '5' ", 'x = 0b10101'
        ]
        for src in data:
            tlines = splitLexems(src)
            clines = elemStream(tlines)
            line0 = clines[0]
            expr = line2expr(line0)
            ctx = Context(None)
            expr.do(ctx)
            res = ctx.get('x')
            # dprint('#a7 ===> ', res.get(), res.getType())





if __name__ == '__main__':
    main()
