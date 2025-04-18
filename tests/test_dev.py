

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
from eval import rootContext

from tests.utils import *

import pdb


class TestDev(TestCase):





    def _test_elem_to_dict_operator(self):
        ''' both cases of `<-` operator for dict
        '''
        code = r'''
        nn = [1, 2, 3]
        keys = ['a','b','c']
        nr = {}
        for i <- [0..2]
            nr <- (keys[i], nn[i])
        print('nr:', nr)
        rr = []
        for key, val <- nr
            rr <- key
        print('rr:', rr)
        '''
        _ = r'''
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('nr').get()
        self.assertEqual({'a' : 1, 'b' : 2, 'c' : 3}, rvar.vals())

    def _test_barr(self):
        ''' '''
        code = r'''
        res = 0
        
        print('res = ', res)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())

    def _test_match_for_if_lambda(self):
        ''' '''
        code = r'''
        c = 5
        res = 0
        func foo2(ff)
            ff(11)
        rrs = [0 ; x <- [0..11]]
        f = x -> x * 10
        for i <- [1..10]
            match c
                1 !- res = 10
                2 !- if res > 0
                    res *= 10
                3 !- res = foo2(x -> x ** 2)
                4 !- f = x -> x * 100
                5 !- for i=0; i < 5; i += 1
                    res += i
                _ !- res = 1000
            rrs[i] = res

        # foo = (x, y) -> x ** 2
        # nums = foo(5, 2)
        print('rrs = ', rrs)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_by_strings(self):
        '''   '''
        code = '''
        src = ['aaa', 'bbb', 'ccc']
        nums = [x ; ns <- src; x <- ns ; x % 5 > 0]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_comprehention_iter_by_string(self):
        ''' list generator and strings
            case 1: list from string
            case 2: string from string ? 
             -- think about: string is a list of chars, but string is an immutable list
        '''
        code = '''
        src = ['a' .. 'k'] # >> 'abcdef...k' ?? do we need that?
        src = "Hello strings!"
        res = [ [a ; a <- src]
        # print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_list_gen_empty_end(self):
        ''' list generator. [... expr;] empty last sub-case after semicolon'''
        code = '''
        nums = [[x ** 2] ; x <- [2..5] ;]
        nums = [[x ** 2] ; x <- [2..5] ; ]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_tuple_assign_left(self):
        ''' make vars and assign vals from tuple
            
            A) tuple as a result of comma-separated expression: var = a, b, c
            Shuold do:
            1. any value-returning sub-expression, like list constructor
            2. think about common case of `x, x, x` expression; not sure.
            tuple as destination of assignment operator, or: result-to-tuple mapping
            Should do:
            1. reuse defined vars.
            2. declare new vars
            3. allow `_` var
            4. allow type declaration (a:int, b:float) = foo()
            Should not:
            1. contain non-var expressions, like func call, collection constuctors (except tuple), const expr like strings or numbers.
            2. contain incorrect var-type
            -- Thoughts:
                a) left-tuple should have extra property like self.isLeft. 
                    In such case tuple can allow call tuple.setVal(args...)
                b) isLeft sould be changable only in assertion operator in .setArgs method.
                c) mapping list to tuple with the same size looks ok.
            '''
        code = '''
        (a, b, s) = 1,2,3
        print('', a, b, c)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_struct_anon(self):
        code = '''
        user = struct {name:'Anod', age:25, sex:male, phone:'123-45-67'}
        # uf = user.fields()
        print(user.name)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_bin_opers_cases(self):
        ''' test all operators in mixed cases: 
            assignment, math | bool expressions, separators (, ; :), brackets. '''


    _ = '''
        TODO features:
        1. generators extra features
    [-10..10]; [..10] >> IterGen(beg, over, step)

        3. tuple
        
        TODO tests:
    test assignment and read 
    global var and local block
    local var and function-block
    
    '''

if __name__ == '__main__':
    main()
