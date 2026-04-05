


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
        
        TODO:? class Null() -> class Null(Val)
        
        TODO (?):  # partially called, make function with remined args; can't be applyed to func with arg...
            foo(1,2, ...>)
            foo(1,2, ->)
            foo(1,2, _...)
            foo(1,2, :...)
            foo(1,2, |...)
            foo(1,2, /...)
            Thoughts: lokos like curried function can do the same;
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
                should we disallow overloading function in another module?
                looks like overloading is a feature within one module
            (? do we need) overloaded methods of imported structs
            
        TODO: override of overload:
                Think about case with same name func in a child is overloaded for another args in parent
                    1) child method will override all overloaded or
                    2) child method will add and shoud find func by signature in all parent tree or
                    3) disallow override overloaded func name
        
        TODO: error if try to curry func with overloading, variadic args. question: how to do with default args.
        
        TODO: error of composition of functions with more than 1 arg
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO:? var type in for-loop 
            for n:int <- nn

        TODO:not. think about type casting by colon; type in left
            x:int = int: true
            # type-constructor is enough 
        
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
        
        TODO: to think: change const from left-modifier to right-operand of `:`
            var : const = val # const elem
            var : const(int) = val # strict typed const elem
        
        BUG: if we have predefined list / dict and try to use same name in the iterative assign by `<-` it breaks code
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
        
        DONE: deprecate list/dict <- append operator inside of comprehension
        
        TODO (?): add explicit append operator: list << val, dict << val. to use into comprehensions  
            alters:   <:  <=  <--  <<  
        
        TODO: match-case: assign val in pattern
            var @ [1, 2, v2 @ _] /: print(var, v2)
            `x @ _` the same as simple var-pattern `x` that matches any single value
        
        TODO: think about deletion of var by name
            delete(x); del(x)
            --- x ; -/- x
            @delete x; @del x
        
        DONE: dict-gen
            dict2 = { k: v + 10 ; k, v <- dict1; v > 0 && k != ''}
        
        TODO: bytes generator: 0x[(n << 2) % 0xff ; n <- iter(32)]
    '''

    _ = r"""
# guides
res = []

"""


    
    

    
    def test_bytes_gen(self):
        '''
        test comprehension generator of bytes
        0x[byte(); n <- src ; ? ]
        '''
        code = r'''
        res = []
        
        # simplest
        ss1 = [1..8]
        r1 = 0x[ n ; n <- ss1]
        res <- r1
        
        
        # by list of bytes
        ss2 = [0x[11 22], 0x[33 44], 0x[aa bb], 0x[ee ff]]
        r2 = 0x[ n ; n <- ss2]
        res <- r2
        
        # by iter gen
        ss3 = [0xff8 .. 0xfff]
        r3 = 0x[n % 255 ; n <- ss3]
        res <- r3
        
        # 2 loops + assign
        ss4 = [(4, 1), (2,205), (4, 64), (4, 252)]
        r4 = 0x[ x ; n, v <- ss4 ; k <- iter(n) ; x = v + k]
        res <- r4
        
        # filter
        nn5 = [128 .. 144]
        r5 = 0x[n ; n <- nn5 ; n % 2 != 0 && n % 3 != 0]
        res <- r5
        
        # filter by func call
        func f6(x, nums)
            for n <- nums
                if x % n == 0
                    return false
            return true
        
        nn6 = [145 .. 196]
        div = [2,3,5,7, 11, 13, 17, 19, 23]
        r6 = 0x[n ; n <- nn6 ; f6(n, div)]
        res <- r6
        
        # by bytes
        bb7 = 0x[1 2 3 4 5 6 7 8 9 a b c d e f]
        r7 = 0x[xb + b ; b <- bb7 ; xb = b * 16 ; b > 7]
        res <- r7
        
        # blocks by bytes
        bb8 = bytes('ABCDEFGHIJKLMNOP')
        r8 = 0x[bytes([c + 32, 0x20]) ; c <- bb8]
        s8 = r8.string()
        res <- r8
        res<- s8
        
        # from struct fields
        struct A nn:list, tt:tuple
        
        a9 = A(
            [1,2,3,4], 
            (bytes('a'), bytes('h'), bytes('m'), bytes('x') ))
        # res <- [0x[ y ; y <- [ n + 0x30,  b]] ; n, bb <- a9.nn, a9.tt ; b = bb[0]]
        
        r9 = 0x[ 0x[ y ; y <- [ n + 0x30,  b]] ; n, bb <- a9.nn, a9.tt ; b = bb[0]]
        res <- r9
        res <- r9.string()
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            '0x[01 02 03 04 05 06 07 08]', 
            '0x[11 22 33 44 aa bb ee ff]', 
            '0x[08 09 0a 0b 0c 0d 0e 0f]', 
            '0x[01 02 03 04 cd ce 40 41 42 43 fc fd fe ff]', 
            '0x[83 85 89 8b 8f]', 
            '0x[95 97 9d a3 a7 ad b3 b5 bf c1]', 
            '0x[88 99 aa bb cc dd ee ff]', 
            '0x[61 20 62 20 63 20 64 20 65 20 66 20 67 20 68 20 69 20 6a 20 6b 20 6c 20 6d 20 6e 20 6f 20 70 20]', 
            'a b c d e f g h i j k l m n o p ', 
            '0x[31 61 32 68 33 6d 34 78]', 
            '1a2h3m4x']
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

