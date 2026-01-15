
import unittest
from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from cases.utils import *
from tree import *
from eval import *
import pdb


# TODO: add asserts to each test

class TestLang(TestCase):



    def _test_type_nums(self):
        code = '''
        a: int = 5
        b: float = 10
        c = b / a
        # print(c, type(c))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        # print('##################t-IF1:', )
        self.assertEqual(res, 45)

    def test_parsing_string_backtiks(self):
        ''' ` string `
            '''
        code = r'''
        res = `1 \n 2 \t3 \s\w\d\b \ \/ \` \' \" `
        # mres = ``` \n \t \\ \s \w ```
        1
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        ex = r'''1 \n 2 \t3 \s\w\d\b \ \/ ` \' \" '''
        self.assertEqual(ex, rvar.getVal())
        # Multiline case wasn't implemented
        # mvar = ctx.get('mres')
        # mex = r''' \n \t \\ '''
        # self.assertEqual(mex, mvar.getVal())

    def test_parsing_lead_minus(self):
        ''' x = -1 * n
            '''
        code = '''
        n = 5
        x = -1 * n
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('x')
        self.assertEqual(-5, rvar.getVal())

    def test_null_struct(self):
        ''' null, val, var, structVar = null '''
        code = r'''
        re = []
        struct A a:int
        
        func foo()
            null
        
        a = A{a:1}
        a = null
        
        b = null
        c = b
        d = foo()
        e = [null]
        f = e[0]
        g = [1]
        g = null
        h = {'h':1}
        h = null
        
        res = [a, b, c, d, f, g, h]
        
        
        # print('res = ', res)
        '''
        
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        exp.do(ctx)
        rvar = ctx.get('res').get()
        exp = [Null(), Null(), Null(), Null(), Null(), Null(), Null()]
        # # dprint('exp', exp)
        # print('res', rvar)
        res = rvar.vals()
        for i in range(max(len(exp), len(res))):
            self.assertEqual(type(exp[i]), type(res[i]))
            self.assertEqual(exp[i].val, res[i].val)

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
            # print(res)
        
        # print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        # ctx.print()
        res = ctx.get('res')
        # dprint('tt>', res.getVal())
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
        # ctx.print()
        res = ctx.get('res')
        # dprint('tt>', res.getVal())
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
        
        # print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        # ctx.print()
        res = ctx.get('res')
        # dprint('tt>', res.getVal())
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
        # print('res=', dd)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        # ctx.print()
        res = ctx.get('res').get()
        # dprint('tt>', res.vals())
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
        # print('res=', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        # dprint('tt>', res.get())
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
        
        # res = foo(1,2,3)
        
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
        
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        print('tt>', res)
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
            # dprint('tt> ', res, code)
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
            ex = tryParse(code)
            ctx = rootContext()
            # dprint('$$ run test ------------------')
            trydo(ex, ctx)
            mstr1 = ctx.get('mstr')
            res = mstr1.getVal()
            # print('EXP:', f'|{expVal}|')
            # print('RES:', f'|{res}|')
            # for i in range(0, 132, 40):
            #     print(i, i+40)
            #     print('#tt e>', [s for s in expVal[i:i+40]])
            #     print('#tt r>', [s for s in res[i:i+40]])
            for i in range(len(expVal)):
            #     print(' i: %d / `%s`<>`%s` ' % (i, res[i], expVal[i]))
                self.assertEqual(res[i], expVal[i], ' i: %d / `%s`<>`%s` ' % (i, res[i], expVal[i]) )
            self.assertEqual(expVal, res)

    def test_multiline2(self):
        ''' Simple smoke-test of correct parsing. '''
        fpath = filepath('parser.et')
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            for tl in tlines:
                dprint('tl>> ', tl.src, '\n :>> ', 
                      ' , '.join([ '`%s`:%s' %(xx.val, Lt.name(xx.ltype)) for xx in tl.lexems]))
            clines:CLine = elemStream(tlines)

    def test_type_nums(self):
        code = '''
        a: int = 5
        b: int = 10
        c = b * a
        # print(c, type(c))
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
        dd = {}
            'red' :'#ff0000'
            'green' :'#00ff00'
            'blue' :'#0000ff'
            'orange' :'#ff8800'
            
        dd['blue'] = 'dark-blue'
        res = []
        for n <- ['red', 'green', 'blue']
            res <- (n, dd[n])
        # print(res)
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        # dprint('$$ run test ------------------')
        exp.do(ctx)
        rvar = ctx.get('res').get()
        expval = [('red', '#ff0000'), ('green', '#00ff00'), ('blue', 'dark-blue')]
        self.assertEqual(expval, rvar.vals())

    def test_dict_construct(self):
        # one-line
        code = '''
        dd = {'aa': 'hello AA', 'bb': 123}
        dd['bb'] = 333
        dd['cc'] = 555
        # print(dd['aa'], dd['bb'] + dd['cc'])
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        # dprint('$$ run test ------------------')
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
            # dprint(code, exp)
            # continue
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = cd.match(elems)
            # self.assertEqual(res, exp)
            # dprint('## t:', code, exp, '>>>', res)

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
            # dprint('## t:', code, exp, '>>>', ind, res.text)
            self.assertEqual(res.text, exp)

    def test_multiline_commets(self):
        code = '''
        # x = 1
        # one line comment
        #@ line1
        multiline comment
        @#x = 5 + 2
        # print(x)
        '''
        code = '''
        a = 10 # first arg
        b = 3 #@  second arg  @#
        x = a + b #@ inline comment @# - 5
        # print(x)
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        # dprint('$$ run test ------------------')
        exp.do(ctx)

    def test_str_in_fun(self):
        code = 'print("Hello buhlo 123!")'
        code = 'st =\'aaa\' + "Hello buhlo 123!" + \'bbb\''
        tlines = splitLexems(code)
        # dprint('lexems', [x.val for n in tlines for x in n.lexems ])
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)

# TODO: check what func uses instead of `afterNameBr`
    # def _test_afterNameBr(self):
    #     data = [
    #         ('arr[1] + ','+'),
    #         ('arr[index] = foo(123)','='),
    #         ('var = 11','='),
    #         ('var += 12','+='),
    #         ('var -= 13','-='),
    #         ('var[ii] += 14','+='),
    #     ]
        
    #     for code, exp in data:
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         ind = afterNameBr(elems)
    #         res = elems[ind]
    #         dprint('## t:', code, exp, '>>>', res.text)
    #         self.assertEqual(res.text, exp)

    #     data = [
    #         ('arr[1]', -1),
    #         ('arr[1+2]', -1),
    #         ('arr[foo(123)]', -1),
    #         ('foo()', -1),
    #         ('foo(123)', -1),
    #         ('foo(a,b,c)', -1),
    #         ('foo(bar())', -1),
    #         ('foo(arr[1])', -1),
    #         ('foo(arr[2],foo(a, arr[3]), b, c)', -1),
    #     ]
        
    #     dprint('#t ------------- no tail')
    #     for code, exp in data:
    #         dprint('#t code: ', code)
    #         tlines = splitLexems(code)
    #         clines:CLine = elemStream(tlines)
    #         elems = clines[0].code
    #         res = afterNameBr(elems)
    #         # res = elems[ind]
    #         dprint('## t:', code, exp, '>>>', res)
    #         self.assertEqual(res, exp)

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


    def test_elem2var(self):
        data = ['123', '0123', '0b1111', '0o777', '0xfba01', '0.15', 
                '1.2j3.5', '1j2.3', '2.3j4', '1.j0.5', '2.5e7', '3.5e-4']
        for d in data:
            res = numLex(d)
            # dprint('', res.get(), res.getType().__class__.name)

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
                # dprint(lx.val)
                if lx.mark == Mk.line:
                    # dprint(','.join(s))
                    s = []
                    # dprint('')
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
            # dprint('#tt>> ',code, ' : ', [n.val for n in parsed])
            self.assertEqual(res, exp, '%s != %s ' % (';'.join(res), exps))
    
    def test_split_oper(self):
        args = ['=++', '++=', '!=-', '-=!', '()++', '()=>()', '++;(-)', '=[-()]']
        for tt in args:
            res = splitOper(tt)
            # dprint('', tt, res)
    
    def test_split_line(self):
        ''' '''
        args = [
            ('for a=10,b=3; i <- 10..20', []),
            ('str2 = ["Hello 3 men!", "123,465 \'-=#=-\'", "\\\'A\\\' + \\\"B\\\"" ]', []),
        ]
        for tt in args:
            src, exp = tt
            # dprint('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
            # res, etype = splitLine(src)
            lastType, extArg = Lt.none, {}
            res, etype, r3 = splitLine(src, lastType, **extArg)
            # dprint([n.val for n in res.lexems])
            # dprint([(n.val, n.mark, n.ltype) for n in res.lexems])

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
        # dprint('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
        for tt in args:
            rt = charType(([], tt[1]), tt[0])
            # dprint("Args: '%s', %s; exp: %s ? %s" % (tt[0], Lt.name(tt[1]), Lt.name(tt[2]), Lt.name(rt)))
            errmsg = "Args: '%s', %s, %s res = %s" % (tt[0], Lt.name(tt[1]), Lt.name(tt[2]), Lt.name(rt))
            self.assertEqual(rt, tt[2], errmsg)
            

if __name__ == '__main__':
    main()
