


from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
# import context
from context import Context
from bases.strformat import *
# from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from bases.over_ctx import FuncOverSet
from tests.utils import *
from libs.regexp import *
from nodes.func_features import *


import cProfile as prof
import pdb

            
class TestDev(TestCase):


    r'''
  _<-od
 (+a)/(-b)
        
        
        TODO:? class Null() -> class Null(Val)
        
        TODO(?): check print of dict: do we need space between pairs or key:val,
        
        TODO: check var is defined 
            defined(var) # as a function
            @defined{var}; @defined(var) # as a service feature
        
        TODO: define local var instead reassign upper-level var
        k = 1
        func foo()
            local k = 5
            @! k # delete local only
        
        TODO: interactive mode:
            $ py lisapet
            >> code...
            remember indent, backspace by indent size
            interpret after and of current top-block
            navigate through code, edit mode (looks like vim)
            # sol_1: python idlelib ?
        
        TODO: overload: 
            test overloading for imported functions, 
                should we disallow overloading function in another module? yep
                looks like overloading is a feature within one module
            (? do we need) overloaded methods of imported structs? nop
            
        TODO: override of overload:
                Think about case with same name func in a child is overloaded for another args in parent
                    1) child method will override all overloaded or
                    2) child method will add and shoud find func by signature in all parent tree or
                    3) disallow override overloaded func name
            
        TODO: prevent overloading of func with default/named args or variadic list args...
        
        TODO: error if try to curry func with overloading, variadic args. 
            question: how to do with default args? disable it
        
        TODO: error of composition of functions with more than 1 arg
        
        TODO: 
            think about escapes in triple-backticks strings
            unary backtick tested in test_parsing_string_backtiks
            mres = ``` \\n \\t \\ \\s \\w ```
        
        TODO: type() for user defined types
            struct ABC a: int, b: int
            abc = ABC{a:1, b:2}
            res <- type(abc)
        
        TODO: check type of operand for all operators
        
        TODO: inspect and resolve MatchPtrCase to avoid use tree.raw2done if not needed anymore
        
        TODO: think about special type for methods. 
            It can simplify check of tail recursion for case with similar names
            maybe )
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO: check and optimize if need Function.checkTail process
        
        TODO: bytes.replace({old:new,...}) # replace by table in dict, overloading replace
        
        TODO: add builtin compare() for base type: string, tuple, bytes.
        
        TODO: string.replace({dict}) # check, implement if not
        
        TODO: add assertion to cases in test_lists
        
        TODO: math functions:
            log(x, base), ln(x), lg(x),
            abs(), sum(list), prod(list), rem(a, b)->>(int, int)
            sin(), cos(), tg(), ctg(), atg(), actg(), asin(), acos(),...
        
        TODO: think about import native lib / module into LP code.
            eval.py: importLib('math', math)
            code.et: import python.math
            
        TODO: think about pattern matching in comprehensions condition

        TODO: outer value: var/const/regexp in pattern matching:
            name = 'Vasya'
            match n
                {name} /: ...
                $name /: ...
                @name /: ...
                'Vasya' /: ...
        
        TODO: range syntax (haskell like)
            [begin .. end] # already done
            [2, 1..5] [step, begin .. end]
            [-1, 5 .. 1] # check after positive custom step
            or
            [a .. b; 2] # [start .. end ; step]
        
        TODO: operator of divisibility
        a ?% b :the same as: a % b == 0
        a !% b :the same as: a % b != 0
        a and b should be an int, b != 0
        
        
        TODO: operator of double-side comparison
            1 < x < 10 :equals: 1 < x && x < 10
            x <= 5 < y
            a < b < c
            a > b > c
        
        TODO?: complex type: some(int)
            it looks hard to implement, 
            in fact it should be a fully implemented type-system with generics or parameterized types.
            More reasons are needed for beginning to work of such complex feature.
            reasons:
            1) maybe(type) / maybe<int> / maybe[int], maybe{int}, maybe int, 
            2) list(int) / [int], dict(type, type) / {string: int} / [string: int],
            3) function(int, string) / function[int, string]
             
            
        TODO: dict.map(func) # looks meaningful
            {1:11, 2:22}.map(\k, v -> (k, v + 10) )
            keyMap: {...}.keyMap(func)
            valmap: {...}.valMap(func)
    '''

    _ = r"""
# guides


"""



    def _test_code(self):
        ''' '''
        code = r'''
        res = []
        
        ss1 = [1..9]
        res <- ss1[2:7]
        
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
        print(resv)
        exv = []
        # self.assertEqual(exv, resv)


    def _test_barr(self):
        ''' '''
        code = r'''
        res = 0
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        self.assertEqual([], rvar.vals())


    def _test_print_struct(self):
        ''' '''
        code = r'''
        struct A a:int
        struct B(A) b:string
        
        
        a = 11
        b = 12.5
        c = false
        d = null
        e = 'str-abc'
        aa = A{a:1}
        bb = B{a:111, b:'B-b-b'}
        
        print('res = ', res)
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
        self.assertEqual(0, rvar.getVal())





class TT:
    def __init__(self):
        self.nodes = [] # [iter, ]
        self.ctx = []
        self.active = True
        self.val = -1
    
    # def start(self):
    #     self.ctx = 
    
    # def preStrp(sel):
    #     1
    
    def add(self, node):
        self.nodes.append(node)
    
    def cond(self, a, b, c):
        return ((a * c) + b) % 5
    
    # def step(self):
    #     for nc in self.nodes[-1]:
    #         if 
        
    
    def get(self):
        return self.val


def gen(a, b, c, fn):
    for ai in a:
        for bi in b:
            for ci in c:
                if fn(ai, bi, ci) % 5 == 0:
                # if True:
                    yield (ai, bi, ci, fn(ai, bi, ci))

class T(TestCase):
    
    def _test_2(self):
        # tt = TT()
        # tt.add(iter(range(5)))
        # tt.add(iter(range(10, 20, 2)))
        # tt.add(iter(range(6,9)))
        
        r = []
        
        def ff(aa, bb, cc):
            return (aa * cc + bb)
        
        a = list(range(5))
        b = list(range(11, 15))
        # c = (n for n in [2,3,5,7])
        c = [2,3,4,5]
        gg = gen(a, b, c, ff)
        
        for n in gg:
            print('>>', n)
        
        # while tt.active:
        #     r.append(tt.get())
        #     tt.step()


if __name__ == '__main__':
    main()

