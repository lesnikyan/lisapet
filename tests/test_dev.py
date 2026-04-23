


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
 (+a)(-b)
        
        
        

        # (?) features for `enum` - not sure
            TODO: Enum.name(11)
            TODO: Enum.value(name)
            TODO: Enum methods .names(), .values(), .items() > (name, val), .todict()
            TODO: 22 ?> Enum # after methods

        TODO:? add shorten alias for the struct: stru A a:int
            shorten of string: name:strn
        
        TODO:? to think about things that is not obvious:
            - instance of function inside function itself
            - additional properties of function as an object
        
        TODO: (?) add byte: int/4, unsigned
            x:byte = 1 # 0-255
            x:byte = 0xff ; auto casting
            x:byte= intVal % 0x100
            #  optional: explicit byte value
            x = &01; 8xff; 8b100; &0xff; |xf0; 8d255
            0xff; 0b10000001
        
        TODO: (?) bytes 0x[01 02 0f] oper shift: bb << 4; bb >> 8 # no extend size
            # we can do the same by slice and adding zero-bytes
        
        TODO:? class Null() -> class Null(Val)
        
        TODO (?):  # partially called, make function with remined args; can't be applyed to func with arg...
            foo(1,2, ...>)
            foo(1,2, ->)
            foo(1,2, _...)
            foo(1,2, :...)
            foo(1,2, |...)
            foo(1,2, /...)
            Thoughts: looks like curried function can do the same;
            func foo(a,b,c)...
            f = foo(1, 2); f(3) ;; g = foo(1); g(2, 3) # partial call
            f = foo~>(1)(2); f(3) ;; g = foo~>(1); g(2)(3)
        
        TODO:? var type in for-loop 
            for n:int <- nn
        
        TODO: (?) think about ?> for bytes, not sure

        TODO: nop. think about type casting by colon; type in left
            x:int = int: true
            # type-constructor is enough 
        
        TODO (?): to think: change const from left-modifier to right-operand of `:`
            var : const = val # const elem
            var : const(int) = val # strict typed const elem
        
        TODO (?): put - inherit / include / mixin of a grup into an another grup
            grup Auch
                x = 1
            
            grup Boo
                put Auch # copy and place here all things from Auch
            
            # not sure, maybe simple encapsulating will be enough:
            grup Boo
                au = Auch
        
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
        
        TODO: fix print(bool): should be false, true, instead of False, True
        
        TODO: add assertion to cases in test_lists
        
        TODO: math functions:
            log(x, base), ln(x), lg(x),
            abs(), sum(list), prod(list), rem(a, b)->>(int, int)
            sin(), cos(), tg(), ctg(), atg(), actg(), asin(), acos(),...
            ceil(), floor(), round()
        
        TODO (?): explicit append operator: list << val, dict << val. to use into comprehensions  
            alters:   <:  <=  <--  <<  
        
        TODO: outer value: var/const/regexp in pattern matching:
            name = 'Vasya'
            match n
                {name} /: ...
                $name /: ...
                @name /: ...
                'Vasya' /: ...
        
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
        
        DONE: fix iter() for down-iteration and negative step
        
        DONE: py -m run -c "print([1..5][:])"
            Error handling:  'ListGenIterator' object has no attribute 'len'
            DONE: add constructor list([1..5])
            DONE: add implicit conversion [..] to list before slice
            
        TODO: think about pattern matching in comprehensions condition
        
        TODO: think about import native lib / module into LP code.
            eval.py: importLib('math', math)
            code.et: import python.math
        
        TODO: add function / (like yeald in py)
            func foo(x)
                for i <- iter(x)
                    res = i * 2
            
            for n <- foo(5)
                n # ...
        
        TODO: method / object as a generator 
            
            struct Generator
            func Generator init()
            func Generator get()
            func Generator next()
            # **
            struct IntGen(Generator) value:int, start:int, fin:int, diff:int 
            func IntGen(x)
                IntGen{start:0, fin:x, diff:1}
            func IntGen(s, f)
                IntGen{start:s, fin:f, diff:1}
            func IntGen(s, f, d)
                IntGen{start:s, fin:f, diff:d}
            
            func g:Generator init()
                g.value = g.start
            func g:Generator get()
                g.value
            func g:Generator next()
                g.value += g.diff
                g.value < g.fin # hasNext (?)
            
            # ***
            struct Gen(Generator) fin:int
            
            # func gen:Gen get()
            #     gen.value
            
            func gen:Gen next()
                if gen.value >= gen.fin
                    gen.stop()
                gen.value += -1
            
            # ***
            gg = Gen(5)
            for n <- gg
                n # 0 1 2 3 4 
            
            TODO?: yield gen
                func f()
                    for n <- [1..5]
                        yield n
            
            TODO?: yield compr gen
                ( n ; n <- [1..5] ) # generator, not a tuple comprehension 
                [yield n ; n <- [1..5]] 
                [: n ; n <- [1..5]] 
                Looks like (;;) is enough
        
        TODO: range syntax (haskell like)
            lazy producer of numeric sequence
            [begin .. end] # already done
            [2, 1..5] [step, begin .. end]
            [-1, 5 .. 1] # check after positive custom step
        
        TODO: add (;;) lazy generator of sequence, 
            can be used in loop, comprehention, sequence constructor
            ( ; ; )
            for n <- (x ; x <- nums ; x > 2)
            list(((x ; x <- nums ; x > 2))) # think about skippng internal brackets
            gen = (x ; x <- nums ; x > 2)
            [n * 10 ; n <- gen]
        
        TODO: split comprehensions (should return collection/sequence)
                and generator (return iterative object)
                
        
        # BUG: ['1:2-.-.>', '1:3-.-.-.-.-.>', '1:2-.-.-.-.-.-.-.>', '1:3-.-.-.-.-.-.-.-.-.-.>', '1:2-.-.-.-.-.-.-.-.-.-.-.-.>',
        # g7 = (: ~'1:{d}' + ~['-'; _ <-iter(d)] + '>' ; a <-[1,2,3]; b <-[5..7]; c <-['','']; d <-[2,3])
        
        #BUG: [[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
        # g7 = (: list(iter(d))  ; a <-[1,2,3]; b <-[5..7]; c <-['','']; d <-[2,3])
        
        
        TODO: next test: generator in the comprehensions list, dict, etc
        
        TODO: multisource for iteration in generator
        (: a + b ; a, b <- aa, bb)
        
        TODO: operator of divisibility
        a ?% b :the same as: a % b == 0
        a !% b :the same as: a % b != 0
        a and b should be an int, b != 0
        
    '''

    _ = r"""
# guides


"""



    def _test_code_generator_in_comprh(self):
        ''' [ ; <- (: <- )] '''
        code = r'''
        res = []
        
        g1 = (: x ; x <- [1..10] ; x % 2 == 0 )
        
        ss1 = [1..9]
        res <- ss1[2:7]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        print(resv)
        exv = []
        # self.assertEqual(exv, resv)
        
    
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

