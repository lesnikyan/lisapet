
import unittest
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
import pdb


# TODO: add asserts to each test

class TestLang(TestCase):


    def test_bool_unary(self):
        ''' test inversion bool. '''
        code = r'''
        func unar(cond)
            inv = false
            if cond && ! inv
                print('inverted')
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

    def test_unclosed_brackets_for(self):
        ''' 
        currently brackets in the `for` statement has strange meaning 
        implement for with brackets. mostly for multiline expressions in `for`.
        It should be the same as case without brackets: init-expr ; if-expr ; post-iter-expr
        `(i=1; i < 10 ; i+=1)` == `i=1; i < 10 ; i+=1`
        '''
        code = '''
        res = 45
        for (i = 1; 
            i <= 10; 
            i +=1
        )
            res += i
            print(res)
        
        print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        ctx.print()
        res = ctx.get('res')
        print('tt>', res.getVal())
        exp = 100
        self.assertEqual(exp, res.getVal())

    def test_unclosed_comprehansion(self):
        '''   '''
        code = '''
        res = 54

        for i <- [ x ** 2 * y ;
            x <- [1..10] ;
            y = (x % 4) + 1 ;
            y > 0        ]
            res += i
            # print(res)
        
        # print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        ctx.print()
        res = ctx.get('res')
        print('tt>', res.getVal())
        exp = 1000
        self.assertEqual(exp, res.getVal())

    def test_unclosed_brackets_if_cond(self):
        '''   '''
        code = '''
        res = 1
        a = 1
        b = 2
        c = 3
        if ( a < b 
            && b > 0
            && c != 5
            )
            res = 100
        
        print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        ctx.print()
        res = ctx.get('res')
        print('tt>', res.getVal())
        exp = 100
        self.assertEqual(exp, res.getVal())

    def test_unclosed_brackets_dict(self):
        '''   '''
        code = '''
        dd = {
            'a':1,
            'b':2
        }
        
        res = dd
        print('res=', dd)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        ctx.print()
        res = ctx.get('res').get()
        print('tt>', res.vals())
        exp = {'a': 1, 'b': 2}
        self.assertEqual(exp, res.vals())


    def test_unclosed_brackets_list(self):
        '''   '''
        code = '''
        aa = [
            'aa aa aa',
            'bb bb bb',
            [1,2,3]
        ]
        
        res = aa
        print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        print('tt>', res.get())
        exp = ['aa aa aa', 'bb bb bb', [1, 2, 3]]
        self.assertEqual(exp, res.get())

    def test_unclosed_brackets_func(self):
        '''   '''
        code = '''
        func foo(
            a, b, 
            c)
            r = a + b
            [r, a, b]
        
        res = foo(
            1,2,
            3
            )
        print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        print('tt>', res.vals())
        self.assertEqual([3,1,2], res.get())

    def test_unclosed_brackets_expr(self):
        
        data = [
            ('(', 1),
            ('foo(', 1),
            ('3 *(2 + ', 1),
            ('foo(1, arg2', 1),
            (' [] + foo ( [], {"":123}, ', 1),
            ('{"aaa":1, "bbb":2', 1),
            ('(1+2) * (b-c', 1),
            ('[[1], [2], [3],', 1),
        ]
        cs = CaseUnclosedBrackets()
        for tt in data:
            code, exp = tt
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            # res = cs.match(clines[0].code)
            # msg = 'src: %s, exp: %s' % (code, bool(exp))
            res = cs.expr(clines[0].code)
            print('tt> ', res, code)
            self.assertIsInstance(res, UnclosedExpr)

    def test_unclosed_brackets_case(self):
        ''' '''
        data = [
            ('(', 1),
            ('foo(', 1),
            ('3 *(2 + ', 1),
            ('foo(1, arg2', 1),
            (' [] + foo ( [], {"":123}, ', 1),
            ('{"aaa":1, "bbb":2', 1),
            ('(1+2) * (b-c', 1),
            ('[[1], [2], [3],', 1),
            
            ('foo()', 0),
            ('123', 0),
            ('varName', 0),
            ('a + b', 0),
            ('1,2,3', 0),
            ('(1,2,3)', 0),
            ('() + [] + {}', 0),
            ('foo([1,2,3], (1+2)*3)', 0),
            ('[1,2,3,foo(4)]', 0),
            ('{[], ([{}, {}]), {}}', 0),
        ]
        
        cs = CaseUnclosedBrackets()
        for tt in data:
            code, exp = tt
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            res = cs.match(clines[0].code)
            msg = 'src: %s, exp: %s' % (code, bool(exp))
            if exp > 0:
                self.assertTrue(res, msg)
            else:
                self.assertFalse(res, msg)

    def test_multiline(self):
        ''' Multiline strings with triple quotes '''
        expVal = '''
        
        string
        content
        ' ' " " ` ` ``` 22 ``` """ 33 """
        '' 1 '' "" 2 "" `` 3 ``
        \t
        \\ / \' \" ` ( +- )
        <a href='main-page.html'>Main page</a>
        '''
        
        expVal = norm(expVal[1:])[:-1]
        fpath = filepath('multilines.et')
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            print('$$ run test ------------------')
            exp.do(ctx)
            mstr1 = ctx.get('mstr')
            res = mstr1.getVal()
            # print('#tt e>', [s for s in expVal])
            # print('#tt r>', [s for s in res])
            # for i in range(len(res)):
            #     self.assertEqual(res[i], expVal[i], ' i: %d / `%s`<>`%s` ' % (i, res[i], expVal[i]) )
            self.assertEqual(expVal, res)

    def test_multiline2(self):
        ''' Simple smoke-test of correct parsing. '''
        fpath = filepath('parser.et')
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            for tl in tlines:
                print('tl>> ', tl.src, '\n :>> ', 
                      ' , '.join([ '`%s`:%s' %(xx.val, Lt.name(xx.ltype)) for xx in tl.lexems]))
            clines:CLine = elemStream(tlines)

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
            # print(exp, sline)
            # continue
            tlines = splitLexems(tsrc)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            pos = spl.mainOper(elems)
            print('tt `%s`' % sline, ' >>> ', pos)
            self.assertEqual(exp, pos)

    def test_colon_vs_other(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        d1 = {'a': 10 + 1}
        struct T1 bb:int
        t1 = T1{bb:4}
        d2 = {'b': 20 / t1.bb}
        
        print(d1['a'], d2['b'])
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
        
    def test_type_nums(self):
        code = '''
        a: int = 5
        b: int = 10
        c = b * a
        print(c, type(c))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('c').getVal()
        self.assertEqual(res, 50)

    def test_struct_field_full(self):
        ''' full test of obj.member cases '''
        code='''
        # object member
        obj.member
        obj.member.member.member
        array[expr].member
        array[expr].member[key].member
        array[expr.member].member
        array[expr].member
        foo(args).member
        obj.fmember()
        obj.fmember(args)
        foo().bar().baz().member
        foo().bar().baz().member.member
        foo().bar().baz().member.method(args)
        array[foo()].member[key].method()
        # --- collection elem
        nums[1][2]
        names[key]['vasya']
        foo(args, [1,2,3]).member.sub[1][2]
        obj.foo(args).member[1][2][3]
        obj.foo1(foo2(foo3([[],[{'a':[[[[1]]]], 'b'[[[[2]]]]}]])))[obj.membr.foo4().name]
        '''
        code = norm(code[1:])
        # code = 'nums[1][2]'
        for line in code.splitlines():
            tlines = splitLexems(line)
            clines:CLine = elemStream(tlines)
            if len(clines) == 0 or len(clines[0].code) == 0:
                continue
            elems = clines[0].code
            # if len(elems) == 0:
            #     continue
            res = isGetValExpr(elems)
            self.assertTrue(res, 'Line >> %s ' % line)

    def test_dict_multiline(self):
        # # multiline
        code = '''
        # create dict var with values in sub-block
        dd = dict
            'red' :'#ff0000'
            'green' :'#00ff00'
            'blue' :'#0000ff'
            'orange' :'#ff8800'
            
        dd['blue'] = 'dark-blue'
        for n <- ['red', 'green', 'blue']
            print(n, dd[n])
        '''
        t='''
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)

    def test_dict_construct(self):
        # one-line
        code = '''
        dd = {'aa': 'hello AA', 'bb': 123}
        dd['bb'] = 333
        dd['cc'] = 555
        print(dd['aa'], dd['bb'] + dd['cc'])
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)

    def test_CaseDictLine_match(self):
        data = [
            ("{}", True),
            ("{'key':'val'}", True),
            ("{a:1, b:2}", True),
            ("{'a':'aa', 'b':22}", True),
            ("{'a':[1,2,3], 'b c d': 2 + 3 - foo(17)}", True),
            ("{'b': data['key'], 'b':arr[12] + num / 2}", True),
            ("(a, b, c)", False),
            ("{a, b, c}", False),
            ("[a, b, c]", False),
            ("{'asd as ds d'}", False),
            ("{a:b:'c'}", False),
            ("{'aa': 'hello dd', 'bb': 123}", False)
        ]
        cd = CaseDictLine()
        for code, exp in data:
            print(code, exp)
            # continue
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = cd.match(elems)
            # self.assertEqual(res, exp)
            print('## t:', code, exp, '>>>', res)

    def test_bracketsPart(self):
        data = [
            ('[(a + (b - c)), nn[10], foo()]', ']'),
            ('[(),[],[[]],([{}])]',']'),
            ('{'':'','':'',(),'':(),'':[]+[]}','}'),
            ('{[],[()], {[]},([]),({[]})}', '}'),
            ("{'aa': 'hello dd', 'bb': 123}", '}'),
        ]

        for code, exp in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            ind = bracketsPart(elems)
            res = elems[ind]
            print('## t:', code, exp, '>>>', ind, res.text)
            self.assertEqual(res.text, exp)

    def test_multiline_commets(self):
        code = '''
        # x = 1
        # one line comment
        #@ line1
        multiline comment
        @#x = 5 + 2
        print(x)
        '''
        code = '''
        a = 10 # first arg
        b = 3 #@  second arg  @#
        x = a + b #@ inline comment @# - 5
        print(x)
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)

    def test_str_in_fun(self):
        code = 'print("Hello buhlo 123!")'
        code = 'st =\'aaa\' + "Hello buhlo 123!" + \'bbb\''
        tlines = splitLexems(code)
        print('lexems', [x.val for n in tlines for x in n.lexems ])
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)

    def test_match_val(self):
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
        print('#t >>> r:', r1)

    def test_CaseMatchSub_match(self):
        cs = CaseMatchCase()
        rrs = []
        def checkRes(code, exp):
            print('$$ run test ------------------')
            print('CODE:','\n'+code)
            # code = lines[0]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = cs.match(elems)
            print('#tt >>> ', code, res)
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
            print('$$ run test ------------------')
            lines = code.split('; ')
            code = '\n'.join(init+lines)
            print('CODE:','\n\n'+code)
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            print('$$ eval expr ------------------')
            exp.do(ctx)
            res = ctx.get('res').get()
            barr = ctx.get('barr').get()
            rrs.append((res, barr,))
        print('# tt>> ', rrs)

    # def _test_CaseBinAssign_split(self):
    #     srcT = '''
    #     x *= 0; res = x
    #     varr += 1; res = varr
    #     arr[2] += 2; res = arr[2]
    #     arr[a + b] += 3; res = arr[a + b]
    #     data[key] += 4; res = data[key]
    #     varr -= 6; res = varr
    #     varr /= 7; res = varr
    #     arr[1] %= 8; res = arr[1]
    #     '''
    #     src = norm(srcT[1:])
    #     data = src.splitlines()
    #     cs = CaseBinAssign()
    #     for code in data:
    #         lines = code.split('; ')
    #         code = lines[0]
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         exp, subs = cs.split(elems)
    #         print('# tt>>>', exp, subs)

    # def _test_CaseBinAssign_match(self):
    #     srcT = '''
    #     x *= 0
    #     varr += 1
    #     arr[2] += 2
    #     arr[a + b] += 3
    #     data[key] += 4
    #     data[foo(arg, arg)] += 5
    #     varr -= 6
    #     varr /= 7
    #     arr[foo(arg)] %= 8
    #     '''
    #     src = norm(srcT[1:])
    #     data = src.splitlines()
    #     cs = CaseBinAssign()
    #     for code in data:
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         res = cs.match(elems)
    #         print('## t:', code, '>>>', res, elems[res])
    #         self.assertTrue(res)
        
    #     srcF = '''
    #     x = 10
    #     y - 11
    #     varr =-12
    #     arr[] = 13
    #     data[key] = 14
    #     varr
    #     12 + 10
    #     foo(...)
    #     [2, 3, 4]
    #     '''
    #     src = norm(srcF[1:])
    #     data = src.splitlines()
    #     cs = CaseBinAssign()
    #     for code in data:
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         res = cs.match(elems)
    #         print('## t:', code, '>>>', res, elems[res])
    #         self.assertFalse(res)

    def _test_afterNameBr(self):
        data = [
            ('arr[1] + ','+'),
            ('arr[index] = foo(123)','='),
            ('var = 11','='),
            ('var += 12','+='),
            ('var -= 13','-='),
            ('var[ii] += 14','+='),
        ]
        
        for code, exp in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            ind = afterNameBr(elems)
            res = elems[ind]
            print('## t:', code, exp, '>>>', res.text)
            self.assertEqual(res.text, exp)


        data = [
            ('arr[1]', -1),
            ('arr[1+2]', -1),
            ('arr[foo(123)]', -1),
            ('foo()', -1),
            ('foo(123)', -1),
            ('foo(a,b,c)', -1),
            ('foo(bar())', -1),
            ('foo(arr[1])', -1),
            ('foo(arr[2],foo(a, arr[3]), b, c)', -1),
        ]
        
        print('#t ------------- no tail')
        for code, exp in data:
            print('#t code: ', code)
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = afterNameBr(elems)
            # res = elems[ind]
            print('## t:', code, exp, '>>>', res)
            self.assertEqual(res, exp)

    def test_seq_split(self):
        data = [
            '1 ,2 ,3',
            'aa, bb, cc',
            '11, aa, foo(1)', 
            '1,22, name, ["aa", "rr", zzz], (one, two, three), foo(bar(1,2,3))', 
            '11, [a,b,c], f() + b(), {a:b, c:d}',
            "'a:' 1 + 2 - foo() , 'b': 1"
        ]
        for src in data:
            tlines = splitLexems(src)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            cs = CaseSeq(',')
        
        
        for src in data:
            tlines = splitLexems(src)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            cs = CaseSeq(',')
            self.assertTrue(cs.match(elems))
            prels('CaseSeq.match: TRUE=%s' % cs.match(elems), elems)
            _, subs = cs.split(elems)
            for sub in subs:
                prels('tt>', sub)

    def test_for_iter(self):
        src = [
        '''
        res = 0
        for i <- iter(10)
            res += i
        print('res: ', res)
        ''',
        '''
        res = 0
        for i <- [1,2,3,4,5,6,7,8,9]
            res += i
        print('res: ', res)
        '''
        ]
        for code in src:
            code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ctx = rootContext()
            ex.do(ctx)
            res = ctx.get('res').get()
            print('##################t-IF1:', )
            # self.assertEqual(res, 45)


    def test_for_expr(self):
        code = '''
        y = 0
        a = 100
        b = 0
        @debug 1
        for i=0; i < 5; i = i + 1
            y = y + 2
            for j=-3; j <= 0; j = j + 1
                a = a - j ** 2
                if a % 2 == 0
                    b = b + 1
        res = y
        '''
        code = norm(code[1:])
        # data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx = Context(None)
            vv = Var('x', TypeInt)
            vv.set(x)
            ctx.addSet({'x': vv})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            rr = [ctx.get('res').get(), ctx.get('a').get() , ctx.get('b').get()]
            ress.append(rr)
            # ress.append(ctx.get('a').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)

    def test_while_expr(self):
        code = '''
        y = 0
        z = 2
        a = 0
        @debug 1
        while y < x
            z = z + z
            y = y + 1
            if y % 2 == 0
                a = a + 1
        res = y
        '''
        code = norm(code[1:])
        # print('!!')
        # print(code)
        # data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx = rootContext()
            vv = Var('x', TypeInt())
            vv.set(Val(x, TypeInt()))
            ctx.addSet({'x': vv})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            ress.append(ctx.get('a').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)


    def test_if_else(self):
        code = '''
        res = 100
        if x >= 10 | x < 2 && x != 0
            res = 2000 + x * -10 - 700
        else
            x = x ** 2
            res = 1000 + x - 500
            # if res < 500
            #     res = res + 10000
        '''
        code = '''
        res = 100
        # y = 0
        if x >= 30 | (x < 2 && x != 0)
            res = 11
        else
            # x = x ** 2
            res = 22
            if res + x > 30
                res = res + x
                res = 33
                @debug 1
                # y = 1
                y = x + res
                res = y
        '''
        # code = ''.join([s[8:] for s in code.splitlines()])
        code = norm(code[1:])
        data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        # data = [10, 20]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx =rootContext()
            vv = Var('x', TypeInt)
            vv.set(Val(x, TypeInt))
            ctx.addSet({'x': vv})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)

    def test_operators_order(self):
        '() [] . , -x !x ~x , ** , * / % , + - , << >> , < <= > >= -> !>, == != , &, ^ , | , && , ||, = += -= *= /= %=  '
        s = 'a = 5 + 6 - 7*(b - c * 10 - 5) / 11 + 3 ** d - 0xe * 5'
        s = 'a = 5 + (2 - 1) * (3 - 4)/ (-1)'
        s = 'a = 5 + sum([1,2,3, b, c + 3])' # TODO: functios
        cs = CaseBinOper()
        for gr in cs.priorGroups:
            print(gr)
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
            print('#t1 mr:', mc, mres)
    
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
            print('#tc11', td, mres)
            ex = elems2expr(elems)
            ex.do(ctx)
            res = ex.get()
            print(' -- #tr11',td, res.getType(), res.get())
    
    def test_CaseUnar(self):
        
        print('##test_CaseUnar True')
        # match true
        data = ['- 5', '-0xa0013bc', '!foo(1,2,ddd)', '!foo(bar(1,2,3, baz("aa a aa")))', '~0xabcdef0011', 
                '~ foo(agr1, arg2)', '-(foo(2-5)+bar(7-num4))']
        
        cs = CaseUnar()
        for td in  data:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            print('#tc11', td, mres)
        
        print('##test_CaseUnar False')
        # match false
        fdata = ['-5 + num1', '-(2+3)-a*b-c', '! val && true', '~ num ^ 0x0011']
        cs = CaseUnar()
        for td in  fdata:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            print('#tc12', td, mres)
    
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
            # ex, subs = cs.split(elems)
            print('#tt1:', mc[0])
            ex = elems2expr(elems)
            ctx = Context(None)
            
            def tvar(k, v):
                print('## tvar:', k, v)
                vv = Var(k, TypeAny)
                vv.set(Val(v, TypeAny))
                return vv
            
            ctx.addSet({k: tvar(k, v) for k, v in mc[1].items()})
            ctx.print()
            ex.do(ctx)
            print('#t-CB1:', ex.get().get())
        

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
            print('#a7 ===> ', res.get(), res.getType())
        

    def test_elem2var(self):
        data = ['123', '0123', '0b1111', '0o777', '0xfba01', '0.15', 
                '1.2j3.5', '1j2.3', '2.3j4', '1.j0.5', '2.5e7', '3.5e-4']
        for d in data:
            res = numLex(d)
            print('', res.get(), res.getType().__class__.name)

    def test_split(self):
        code_input1 = '''
        x = 5
        for i to 15
            print i

        for i << 1..5
            print i
        # for x <- 5..20, 3 | x % 3 > 0 ???
        for a=10,b=3; i <- 10..20
            c = a + b + i
            if n=i*2+1; if n != c
                print c
                fprint('%s %d %f', c, 2, 3)
        '''

        tlines = splitLexems(code_input1)
        s = []
        for tl in tlines:
            for lx in tl.lexems:
                # print(lx.val)
                if lx.mark == Mk.line:
                    print(','.join(s))
                    s = []
                    # print('')
                    continue
                s.append(lx.val)

    def test_parse_numbers(self):
        '''' '''
        # fpath = filepath('parser.et')
        # with open(fpath, 'r') as f:
        text = '''
        11.22 # 11.22
        0xff00 # 0xff00
        1..9 # 1 .. 9
        2:-1 # 2 : - 1
        1,25 # 1 , 25
        0b10101 # 0b10101
        0o123 # 0o123
        11.22.33 # 11.22 . 33
        11.22.cc # 11.22 . cc
        11.22.ss # 11.22 . ss
        11. # 11.
        11.() # 11. ( )
        '''
        src = norm(text[1:]).splitlines()
        for line in src:
            code, exps = line.split('#')
            if len(code.strip()) == 0 or len(exps.strip()) == 0:
                # skip empty case
                continue
            exp = exps.strip().split(' ')
            tlines = splitLexems(code.strip())
            parsed = tlines[0].lexems
            res = [n.val for n in parsed]
            print('#tt>> ',code, ' : ', [n.val for n in parsed])
            self.assertEqual(res, exp, '%s != %s ' % (';'.join(res), exps))
    
    def test_split_oper(self):
        args = ['=++', '++=', '!=-', '-=!', '()++', '()=>()', '++;(-)', '=[-()]']
        for tt in args:
            res = splitOper(tt)
            print('', tt, res)
    
    def test_split_line(self):
        ''' '''
        args = [
            ('for a=10,b=3; i <- 10..20', []),
            ('str2 = ["Hello 3 men!", "123,465 \'-=#=-\'", "\\\'A\\\' + \\\"B\\\"" ]', []),
        ]
        for tt in args:
            src, exp = tt
            print('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
            # res, etype = splitLine(src)
            lastType, extArg = Lt.none, {}
            res, etype, r3 = splitLine(src, lastType, **extArg)
            print([n.val for n in res.lexems])
            print([(n.val, n.mark, n.ltype) for n in res.lexems])

    def test_parsing_list_gen_(self):
        ''' Case where whole expression consists of valid number chars:
            'j', 'x', 'b', 'o',  '.', 'a', 'b', 'c', 'd', 'e', 'f' 
            '''
        code = '''
        
        x = 4
        n = [1..x]
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_lex_type(self):
        ''' charType(prev:int, s:str) '''
        args = [(' ',0,Lt.space), ('\t', 0,Lt.space), ('\n', 0,Lt.space), ('\r', 0,Lt.space), 
                (' ', Lt.text, Lt.text), ('\t', Lt.text, Lt.text),
                (' ',Lt.word,Lt.space),('\t',Lt.word,Lt.space),('\n',Lt.word,Lt.space),
                (' ',Lt.num,Lt.space),('\t',Lt.num,Lt.space),('\n',Lt.num,Lt.space),
                (' ',Lt.oper,Lt.space),('\t',Lt.oper,Lt.space),('\n',Lt.oper,Lt.space),
                (' ',Lt.space,Lt.space),('\t',Lt.space,Lt.space),('\n',Lt.space,Lt.space),
                
                ('a',0,Lt.word),('a',Lt.word,Lt.word),('k',Lt.num,Lt.word),('a',Lt.oper,Lt.word),('a',Lt.text,Lt.text),('a',Lt.space,Lt.word),
                # hex, complex, bin, octa case:
                ('a',Lt.num,Lt.num),('b',Lt.num,Lt.num),('f',Lt.num,Lt.num),('x',Lt.num,Lt.num),('o',Lt.num,Lt.num),('0',Lt.num,Lt.num),
                ('B',0,Lt.word),('B',Lt.word,Lt.word),('B',Lt.num,Lt.word),('B',Lt.oper,Lt.word),('B',Lt.text,Lt.text),('B',Lt.space,Lt.word),
                ('+',0,Lt.oper),('-',Lt.word,Lt.oper),('<',Lt.num,Lt.oper),('>',Lt.oper,Lt.oper),('/',Lt.text,Lt.text),('?',Lt.space,Lt.oper),
                ('0',0,Lt.num),('1',Lt.word,Lt.word),('2',Lt.num,Lt.num),('3',Lt.oper,Lt.num),('4',Lt.text,Lt.text),('5',Lt.space,Lt.num),
                
                ('#',0,Lt.comm),('#',Lt.word,Lt.comm),('#',Lt.num,Lt.comm),('#',Lt.oper,Lt.comm),('#',Lt.text,Lt.text),('#',Lt.space,Lt.comm),
                ('#',Lt.comm, Lt.comm),(' ',Lt.comm,Lt.comm),('a',Lt.comm,Lt.comm),
                ('1',Lt.comm,Lt.comm),('*',Lt.comm,Lt.comm),('\"',Lt.comm,Lt.comm),
                
                ('\\',0,Lt.oper),('\\',Lt.word,Lt.oper),('\\',Lt.num,Lt.oper),('\\',Lt.oper,Lt.oper),('\\',Lt.text,Lt.esc),('\\',Lt.space,Lt.oper),
                ('\\',Lt.esc,Lt.text),('\'',Lt.esc,Lt.text),('\"',Lt.esc,Lt.text),('n',Lt.esc,Lt.text),('r',Lt.esc,Lt.text),('t',Lt.esc,Lt.text),
                ('/',Lt.esc,Lt.text),('`',Lt.esc,Lt.text),
                # ('',Lt),('',Lt),('',Lt),('',Lt),('',Lt),('',Lt),('',Lt),
                ]
        # print('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
        for tt in args:
            rt = charType(([], tt[1]), tt[0])
            print("Args: '%s', %s; exp: %s ? %s" % (tt[0], Lt.name(tt[1]), Lt.name(tt[2]), Lt.name(rt)))
            errmsg = "Args: '%s', %s, %s res = %s" % (tt[0], Lt.name(tt[1]), Lt.name(tt[2]), Lt.name(rt))
            self.assertEqual(rt, tt[2], errmsg)
            

if __name__ == '__main__':
    main()
