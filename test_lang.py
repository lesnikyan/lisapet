
import unittest
from unittest import TestCase, main

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, buildLexems, elemStream
from vars import *
from vals import numLex
from tnodes import Var, Context
from tree import *



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

def norm(code):
    ''' Normalize input code: 
    - cut extra indent'''
    ind = 0
    for s in code:
        # print('`%s`' % s)
        if s == ' ':
            ind += 1
        else:
            break
    print('norm ind=', ind)
    return '\n'.join([s[ind:] for s in code.splitlines()])


class TestParse(TestCase):
    
    def _test_tree(self):
        '''' '''
        res = buildLexems(splitLexems(code_input1))
        for n in res:
            print('%s, %s'%(Lt.name(n.type), n.text))

    def _test_for_array(self):
        ''' for n <- [1,2,x] 
            for n <- arrVar
        '''

    def test_CaseBinAssign(self):
        init = '''
        x = 0
        varr = 2*3*5*7*100
        barr = 2*3*5*7*100
        arr = [0,1,2,32,4,5]
        data = [10,20,30,40,50]
        key = 2
        a = 1
        b = 2
        '''
        srcT = '''
        x *= 0; res = x
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
            print('CODE:','\n'+code)
            # code = lines[0]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            # elems = clines[0].code
            # exp, subs = cs.split(elems)
            # print('# tt>>>', exp, subs)
            exp = lex2tree(clines)
            ctx = Context(None)
            print('$$ eval expr ------------------')
            exp.do(ctx)
            res = ctx.get('res').get()
            barr = ctx.get('barr').get()
            rrs.append((res, barr,))
            
            # ind = afterNameBr(elems)
            # res = elems[ind]
            # res = cs.match(elems)
            # print('## t:', code, '>>>', res, elems[res])
            # self.assertTrue(res)
        print('# tt>> ', rrs)

    def _test_array_set(self):
        src = '''
        a = 1
        b = 2
        val = 10
        arr = [1,2,3,4,5]
        arr[1] = 20
        arr[a+b] = val + arr[1]
        res = arr[a+b]
        '''
        code = norm(src[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = Context(None)
        print('$$ run test ------------------')
        exp.do(ctx)
        res = ctx.get('res')
        print('# tt>> ', res)
        

    def _test_CaseBinAssign_split(self):
        srcT = '''
        x *= 0; res = x
        varr += 1; res = varr
        arr[2] += 2; res = arr[2]
        arr[a + b] += 3; res = arr[a + b]
        data[key] += 4; res = data[key]
        varr -= 6; res = varr
        varr /= 7; res = varr
        arr[1] %= 8; res = arr[1]
        '''
        src = norm(srcT[1:])
        data = src.splitlines()
        cs = CaseBinAssign()
        for code in data:
            lines = code.split('; ')
            code = lines[0]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            exp, subs = cs.split(elems)
            print('# tt>>>', exp, subs)

    def _test_CaseBinAssign_match(self):
        srcT = '''
        x *= 0
        varr += 1
        arr[2] += 2
        arr[a + b] += 3
        data[key] += 4
        data[foo(arg, arg)] += 5
        varr -= 6
        varr /= 7
        arr[foo(arg)] %= 8
        '''
        src = norm(srcT[1:])
        data = src.splitlines()
        cs = CaseBinAssign()
        for code in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            # ind = afterNameBr(elems)
            # res = elems[ind]
            res = cs.match(elems)
            print('## t:', code, '>>>', res, elems[res])
            self.assertTrue(res)
        
        srcF = '''
        x = 10
        y - 11
        varr =-12
        arr[] = 13
        data[key] = 14
        varr
        12 + 10
        foo(...)
        [2, 3, 4]
        '''
        src = norm(srcF[1:])
        data = src.splitlines()
        cs = CaseBinAssign()
        for code in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            # ind = afterNameBr(elems)
            # res = elems[ind]
            res = cs.match(elems)
            print('## t:', code, '>>>', res, elems[res])
            self.assertFalse(res)

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

    def _test_array(self):
        data = [
            '''
            arr = [1,2,3]
            res = arr[0]
            r2 = 1000
            for i <- iter(3)
                r2 = r2 + arr[i]
            ''',
            # ''' ''',
            # ''' ''',
        ]
        # ctdata = {
        #     'a': 1,
        #     'b':2,
        #     'c':3
        # }
        for code in data:
            code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ress = []
            ctx = Context(None)
            # for k, v in ctdata.items():
            #     ctx.addSet({k: Var(v, k, TypeInt)})
            print('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)
            rr = [ctx.get('res').get() , ctx.get('r2').get()]
            print('Test res = ', rr)

    def _test_array_expr(self):
        data = [
            '[1,2,3]', 
            '[a, b, c]',
            # '[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]',
        ]
        ctdata = {
            'a': 1,
            'b':2,
            'c':3
        }
        for code in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ress = []
            ctx = Context(None)
            for k, v in ctdata.items():
                ctx.addSet({k: Var(v, k, TypeInt)})
            print('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)
            # rr = [ctx.get('res').get()]
            # print('Test res = ', rr)

    def _test_seq_split(self):
        data = [
            '1 ,2 ,3',
            'aa, bb, cc',
            '11, aa, foo(1)', 
            '1,22, name, ["aa", "rr", zzz], (one, two, three), foo(bar(1,2,3))', 
            '11, [a,b,c], f() + b(), {a:b, c:d}'
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
            # prels('CaseSeq.match: ', elems)
            if cs.match(elems):
                prels('CaseSeq.match: TRUE', elems)
                _, subs = cs.split(elems)
                for sub in subs:
                    prels('tt>', sub)

    def _test_for_iter(self):
        code = '''
        x = 0
        a = 0
        b = 0
        size = 10
        @debug 2
        if x < 1
            a = 111
        for n <- iter(size)
            x = x + n
            b = b + 1
        res = x
        '''
        code = norm(code[1:])
        # data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        ctx = Context(None)
        # ctx.addSet({'x': Var(x, 'x', TypeInt)})
        # print('~~~~ test case: %d ~~~~' % x)
        ex.do(ctx)
        rr = [ctx.get('res').get(), ctx.get('a').get() , ctx.get('b').get()]
        ress.append(rr)
        # ress.append(ctx.get('a').get())
        print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)

    def _test_for_expr(self):
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
            ctx.addSet({'x': Var(x, 'x', TypeInt)})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            rr = [ctx.get('res').get(), ctx.get('a').get() , ctx.get('b').get()]
            ress.append(rr)
            # ress.append(ctx.get('a').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)

    def _test_while_expr(self):
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
            ctx = Context(None)
            ctx.addSet({'x': Var(x, 'x', TypeInt)})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            ress.append(ctx.get('a').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)


    def _test_if_else(self):
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
            ctx = Context(None)
            ctx.addSet({'x': Var(x, 'x', TypeInt)})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            print('##################t-IF1:', ctx.get('res').get())
        print('all:', ress)

    def _test_operators_order(self):
        '() [] . , -x !x ~x , ** , * / % , + - , << >> , < <= > >= -> !>, == != , &, ^ , | , && , ||, = += -= *= /= %=  '
        # -> in, !> not in: if 12 -> nums, if 'a' !> names. # ??
        # a = 12 % 5;
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
    
    def _test_CaseUnar_split(self):
        data = ['- 5', '-0xa0013bc', '!ddd',  '~0x0abc', '-123456789', '-(-(-num1))', '-(-(-(-(-(-111)))))', '!(!(!(!(!((!true))))))']
        ctxData = {'ddd':True, 'num1':-17}
        cs = CaseUnar()
        for td in  data:
            tlines = splitLexems(td)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            mres = cs.match(elems)
            ctx = Context(None)
            ctx.addSet({v: Var(k, v) for v, k in ctxData.items()})
            print('#tc11', td, mres)
            ex = elems2expr(elems)
            ex.do(ctx)
            res = ex.get()
            print(' -- #tr11',td, res.getType(), res.get())
    
    def _test_CaseUnar(self):
        
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
    
    def _test_CaseBinOper_split(self):
        ''' '''
        data = [
            # ('1+2-3 * 4 + 5'),
            ('5 + 6 - 7*(b - c * 12 - 15) / 11 + 3 ** d - 0xe * 8', {'b':100, 'c':4, 'd':3}) # -97.54545454545455
            # ('5 + (2 - 1) * (3 - 4)/ (1)',{})
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
            ctx.addSet({v: Var(k, v) for v, k in mc[1].items()})
            ex.do(ctx)
            print('#t-CB1:', ex.get().get())
        

    def _test_line_assign(self):
        data = [
            'x = 5.0', 'x = 5j2', 'x = 0xf000a', "x = '5' ", 'x = 0b10101'
        ]
        # src = 'x = 5.0'
        # src = 'x = 5j2'
        # src = 'x = 0xf000a' # 983050
        # src = "x = '5' "
        for src in data:
            tlines = splitLexems(src)
            # print('#a6', [n.val for n in tlines[0].lexems])
            clines = elemStream(tlines)
            # print('#a2', len(clines))
            line0 = clines[0]
            # print('#a1', line0.code)
            expr = line2expr(line0)
            ctx = Context(None)
            expr.do(ctx)
            res = ctx.get('x')
            print('#a7 ===> ', res.get(), res.getType())
        

    def _test_elem2var(self):
        data = ['123', '0123', '0b1111', '0o777', '0xfba01', '0.15', 
                '1.2j3.5', '1j2.3', '2.3j4', '1.j0.5', '2.5e7', '3.5e-4']
        for d in data:
            res = numLex(d)
            print('', res.get(), res.getType().__class__.name)

    
    def _test_split(self):
        ''' '''
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
    
    def _test_split_oper(self):
        args = ['=++', '++=', '!=-', '-=!', '()++', '()=>()', '++;(-)', '=[-()]']
        for tt in args:
            res = splitOper(tt)
            print('', tt, res)
    
    def _test_split_line(self):
        ''' '''
        args = [
            ('for a=10,b=3; i << 10..20', []),
            ('str2 = ["Hello 3 men!", "123,465 \'-=#=-\'", "\\\'A\\\' + \\\"B\\\"" ]', []),
            # ('', []),
            # ('', []),
        ]
        # src = 'for a=10,b=3; i << 10..20'
        # res = splitLine(src)
        # print([(n.val, n.mark, n.ltype) for n in res])
        for tt in args:
            src, exp = tt
            print('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
            res = splitLine(src)
            print([n.val for n in res.lexems])
            print([(n.val, n.mark, n.ltype) for n in res.lexems])
        
    
    def _test_lex_type(self):
        ''' charType(prev:int, s:str) '''
        args = [(' ',0,Lt.space), ('\t', 0,Lt.space), ('\n', 0,Lt.space), ('\r', 0,Lt.space), 
                (' ', Lt.text, Lt.text), ('\t', Lt.text, Lt.text),
                (' ',Lt.word,Lt.space),('\t',Lt.word,Lt.space),('\n',Lt.word,Lt.space),
                (' ',Lt.num,Lt.space),('\t',Lt.num,Lt.space),('\n',Lt.num,Lt.space),
                (' ',Lt.oper,Lt.space),('\t',Lt.oper,Lt.space),('\n',Lt.oper,Lt.space),
                (' ',Lt.space,Lt.space),('\t',Lt.space,Lt.space),('\n',Lt.space,Lt.space),
                
                ('a',0,Lt.word),('a',Lt.word,Lt.word),('a',Lt.num,Lt.word),('a',Lt.oper,Lt.word),('a',Lt.text,Lt.text),('a',Lt.space,Lt.word),
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
        print('space %d, word %d, num %d, oper %d, text %d, quot %d, esc %d' % (Lt.space, Lt.word, Lt.num, Lt.oper, Lt.text, Lt.quot, Lt.esc))
        for tt in args:
            rt = charType(tt[1], tt[0])
            print(tt, rt)
            errmsg = "Args: '%s' %d %d" % (tt[0],tt[1], tt[2])
            self.assertEqual(rt, tt[2], errmsg)
            

if __name__ == '__main__':
    main()
