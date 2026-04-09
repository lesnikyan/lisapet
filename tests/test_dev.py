


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
        
        
        
         
        DONE: const value
            const x: int = 10
        
        DONE: if conditional expr is a last node of function then
            last executed expression (sub-part of conditional) should be a result of function
        func foo()
            if cond
                ...
                expr1 # result
            else if cond
                expr2 # result
            else
                expr3 # result
        func foo()
            match n
                1 /: 10 # result
                2
                    20 # result
                a :: type
                    b = f(a)
                    b + 30 # result
                _
                    50 # default result

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
        
        
        TODO (?): put - inherit / include / mixin of a grup into an another grup
            grup Auch
                x = 1
            
            grup Boo
                put Auch # copy and place here all things from Auch
            
            # not sure, maybe simple encapsulating will be enough:
            grup Boo
                au = Auch
        
        TODO: 
            think about escapes in triple-backticks strings
            unary backtick tested in test_parsing_string_backtiks
            mres = ``` \\n \\t \\ \\s \\w ```
        
        TODO: type() for user defined types
            struct ABC a: int, b: int
            abc = ABC{a:1, b:2}
            res <- type(abc)
        
        TODO: inspect and resolve MatchPtrCase to avoid use tree.raw2done if not needed anymore
        
        TODO: check type of operand for all operators
        
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
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO:? var type in for-loop 
            for n:int <- nn

        TODO: nop. think about type casting by colon; type in left
            x:int = int: true
            # type-constructor is enough 
        
        TODO (?): to think: change const from left-modifier to right-operand of `:`
            var : const = val # const elem
            var : const(int) = val # strict typed const elem
        
        TODO: add assertion to cases in test_lists
        
        TODO: think about import native lib / module into LP code.
            eval.py: importLib('math', math)
            code.et: import python.math
        
        TODO: math functions:
            log(x, base), ln(x), lg(x),
            abs(), sum(list), prod(list), rem(a, b)->>(int, int)
            sin(), cos(), tg(), ctg(), atg(), actg(), asin(), acos(),...
            ceil(), floor(), round()
        
        TODO: bytes.replace({old:new,...}) # replace by table in dict, overloading replace
        
        TODO: string.replace({dict}) # check, implement if not
        
        TODO: fix print(bool): should be false, true, instead of False, True
        
        TODO: add builtin compare() for base type: string, tuple, bytes.
        
        
        TODO: think about special type for methods. 
            It can simplify check of tail recursion for case with similar names
            maybe )
        
        TODO: check and optimize if need Function.checkTail process
         
        DONE: 21.1 Multi-reading in loop:
            put at right part one more collections, so assign more var in left: 
            aa = [1,2,3]
            dd = {11:1, 22:2, 33:3}
            for i, x, key, val <- iter(3), aa, dd
                print(i, x, key, val)
        
        DONE: 21.2 Mult-reading in list-gen:
            [ x + y ; x, y <- nn, mm]
        
        DONE: deprecate list/dict <- append operator inside of comprehension
        
        DONE: dict-gen
            dict2 = { k: v + 10 ; k, v <- dict1; v > 0 && k != ''}
        
        DONE: bytes generator: 0x[(n << 2) % 0xff ; n <- iter(32)]
        
        DONE: match-case: assign val in pattern
            var @ [1, 2, v2 @ _] /: print(var, v2)
            `x @ _` the same as simple var-pattern `x` that matches any single value
        
        FIXED: if we have predefined list / dict and try to use same name in the iterative assign by `<-` it breaks code
            File "C:\Users\admin\Documents\python_examples\minilang\nodes\oper_nodes.py", line 68, in doRight
                src.do(ctx)
            File "C:\Users\admin\Documents\python_examples\minilang\nodes\iternodes.py", line 652, in do
                self.iterLoop(0, ctx)
            File "C:\Users\admin\Documents\python_examples\minilang\nodes\iternodes.py", line 623, in iterLoop
                inod.start()
            == solution: deprecate use list <- val in the generators.
            == solution: add alter operator instead of universal <- .
            == solution: deprecate <- for append elem in generator, 
                add alter oper for explicit append action: << <-- 
        
        DONE: think about deletion of var by name
            @! operator has been implemented
            # delete(x); del(x)
            # --- x ; -/- x ; -= x ; >< x ;
            # @delete x; @del x
            # del x, y, name # non-single expr
            # @del(x, y, name) # single expr
        
        TODO (?): add explicit append operator: list << val, dict << val. to use into comprehensions  
            alters:   <:  <=  <--  <<  
            
        TODO: think about pattern matching in comprehensions condition
        
        TODO: interactive mode:
            $ py lisapet
            >> code...
        
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
        
        TODO: ~[s, s <- "..."] gen by string: 
            solution (1) `~` operator as a list-to-string convertor
            sol(2): ~[;] # string-generator 
            s <- "..." # glif stream from string
            ~[gX ; gX <- string] # join all glifs to string
            [ gX ; gX <- string ] # list of glifs
    '''

    _ = r"""
# guides
res = []

"""


    
    def test_string_comprehension(self):
        ''' '''
        code = r'''
        res = []
        
        
        # List by string

        # list gen from string
        r1 = [ g ; g <- 'abc']
        res <- r1
        
        # list gen mixed source string, list
        a2 = [1,2,3]
        s2 = 'def'
        r2 = [~'{s}{n}' ; s, n <- s2, a2 ; n > 1]
        res <- r2
        
        
        # String from glifs
        
        # from string ~[;  <- '']
        r3 = ~[ s ; s <- 'Hello!']
        res <- r3
        
        # from bytes ~[ ; n <- 0x[]]
        bb4 = 0x[41 42 43 44 21 61 62 63]
        r4 = ~[glif(b) ; b <- bb4]
        res <- r4
        
        # from numbers ~[ ; n <- [41..50]]
        r5 = ~[ glif(n); n <- [80.. 85]]
        res <- r5
        
        
        # String from strings
        
        # from list of sttrings ~[wd ; wd <- ['I', 'am', 'coding']]
        ss6 = ['I', '-', 'am', '-', 'coding']
        r6 = ~[x ; wd <- ss6; x = wd == '-' ? ' ' : wd]
        res <- r6
        
        # from multiline, 2 iterations
        ss7 = """
        Hello!
        What we can do?
        Let's do it!
        """
        r7 = ~[wd + ' ' ; ss <- ss7.split('\n'); wd <- ss.split(re`\b`) ; len(wd) > 0]
        res <- r7
        
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
        # print(resv)
        exv = [['g(a)', 'g(b)', 'g(c)'], ['e2', 'f3'], 'Hello!', 'ABCD!abc', 'PQRSTU', 'I am coding', "Hello ! What   we   can   do ? Let ' s   do   it ! "]
        self.assertEqual(exv, resv)
        
    

    
    def _test_code(self):
        ''' '''
        code = r'''
        res = []
        
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
        


    def _test_match_last_expr_of_case_as_result(self):
        ''' if `match` is a last expression in function. 
            each sub-case of match will return result of their last expression'''
        code = r'''
        res = []
        
        func fsubRes(n)
            # Last expression is a result
            match n
                # indent block
                ::int # some comment
                    x  = 1
                    x
                
                # inline block
                ::bool /: x = 2; x
                
                # /: but indent (it's ok)
                {_:_} /:
                    y = 3
                    y
                
                # block with sub control
                p::(tuple|list)
                    r4 = []
                    for x <- p
                        r4 <- x
                        if len(r4) >= 3
                        # in if/else must use `return`
                            return (4, r4, p)
                    -1000
                # default
                _ /: 5
            # end of function
            
        nn = [1, true, [1,2,3], (3,4,5), {4:44}, 1.5, [100,200]]
        
        for k <- nn
            res <- fbase(k)
            
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # exv = [1, 2, (4, [1, 2, 3], [1, 2, 3]), (4, [3, 4, 5], (3, 4, 5)), 3, 5, -2000]
        # self.assertEqual(exv, rvar.vals())


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



if __name__ == '__main__':
    main()

