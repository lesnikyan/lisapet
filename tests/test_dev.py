


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
        
    # features for for `enum` - not sure
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
        
        TODO: (?) bytes oper shift: bb << 4; bb >> 8 # no extend size
        
        TODO:? class Null() -> class Null(Val)
        
        TODO (?):  # partially called, make function with remined args; can't be applyed to func with arg...
            foo(1,2, ...>)
            foo(1,2, ->)
            foo(1,2, _...)
            foo(1,2, :...)
            foo(1,2, |...)
            foo(1,2, /...)
        
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
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO:? var type in for-loop 
            for n:int <- nn

        TODO: think about type casting by colon; type in left
            x:int = int: true
        
        TODO: error if try to curry func with overloading, variadic args. question: how to do with default args.
        TODO: error of composition of functions with more than 1 arg

        TODO: 21.1 Multi-reading in loop:
            put at right part one more collections, so assign more var in left: 
            aa = [1,2,3]
            dd = {11:1, 22:2, 33:3}
            for i, x, key, val <- iter(3), aa, dd
        
        TODO: group - static block for set of const vals and functions. 
            Like extended enum and struct
                print(i, x, key, val)
        
        BUG: Sequence  match and split if brackets in quotes: (1, '[', ']')
        
        TODO: add assertion to cases in test_lists
        
        
        TODO: think about performance, decreased after \lambda changes.
        
        TODO: bytes generator: 0x[(n << 2) % 0xff ; n <- iter(32)]
        
        TODO: think about import native lib / module into LP code.
            eval.py: importLib('math', math)
            code.et: import math
        
        TODO: math functions:
            log(x, base), ln(x), lg(x),
            abs(), sum(list), prod(list), rem(a, b)->>(int, int)
            sin(), cos(), tg(), ctg(), atg(), actg(), asin(), acos(),...
            ceil(), floor(), round()
        
        TODO: bytes.replace({old:new,...}) # replace by table in dict, overloading replace
        
        TODO: string.replace({dict}) # check, implement if not
        
        TODO: fix print(bool): should be false, true, instead of False, True
        
        TODO: add builtin compare() for base type: string, tuple, bytes.
        
        TODO: refactor tree.py from loops of cases to pattern-tree
        1) find common cases:
            solid -> in-brackets, dot.name, solid(brackets), solid-rUnar, single control-keywords, var, val, 
            no-solid -> definitions, control-statements, bin-opers, 
        2) dive into sub-cases
        2.2) refactor list-like expressions to avoid multiple check items in []-brackets
            first check solid []-case, then find case in []-cases:
            list, slice, iter-gen, list-gen, bytes
    '''

    _ = r"""
# guides


"""


    def test_interpret_mt_cases(self):
        
        data = r'''
        #= solid
        12
        []
        ()
        (,)
        {}
        _{}
        aa{}
        a :: int
        b :: int | float
        c :: A | list
        1 | 2 | 3
        ::A|B|C
        
        () | {}
        :: A
        :: a | int
        :: A | B
        (:: int, )
        [:: int,]
        (:: int)
        
        
        #= bugs
        
        '''
        data = norm(data[1:]).splitlines()
        for src in data:
            if '' == src.strip():
                continue
            if src.startswith('#'):
                continue
            
            # print('>', src)
            # src = src.replace('$/N', '\n')
            src = 'match n\n    %s' % src

            tlines = splitLexems(src)
            # print('', [[(l.val, Lt.name(l.ltype)) for l in n.lexems] for n in tlines])
            clines:CLine = elemStream(tlines)
            # print('', [c for c in clines])
            try:
                expTree:Module = lex2tree(clines)
                MatchExpr, CaseExpr
                # print('tt1>', expTree.subs[0].cases[0].expect.__class__.__name__)
                # print('tt1>', expTree.subs[0].__class__.__name__)
            except LangError as ex:
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n!! Error LangError:', ex.msg)
                self.fail()
                # raise ex
            except Exception as ex:
                # print('`=`=`=`=`=`=`=`\n!!Error Exception', ex.args)
                self.fail()
                # raise ex



    def interpret_base_cases(self):
        
        data = r'''
        #= solid
        12
        12.5
        0xdef
        0b101
        name
        @debug
        return
        break
        continue
        if true$/N    2$/Nelse$/N    3
        _
        obj.aaa
        []
        [1,2,3]
        [2 .. 5]
        [n ; n <- nums; n != 5]
        [11 22 fe]
        0x[12 34 fe dc]
        nums[1]
        nums[1:end]
        [- 100]
        [a * b]
        [[1,2,3]]
        [[]]
        [obj.memb]
        [foo()]
        
        foo(1)
        f1().aaa.f2().bbb[1+2].f3()
        Abc{}
        Abc{a:1}
        'Hello 1'
        `Hello 2`
        foo()
        (1)
        """Hello\n 3"""
        g'A'
        re'[0-9a-f]?[soda]{1,5}'
        re`abc\w+\s+`ui
        ~"Format {a} {f()}"
        foo~>
        args...
        (1,2,3)
        {'a': 'bbb'}
        {a:11, 'b':234, c: [1,2]}
        (a + b - 13 / 44 * foo() - obj.val)
        foo~>(1)(2)
        true
        null
        
        #== not solid
        a + b
        a = 13
        a = a + b
        func foo()
            1
        
        struct Abc a:int, b:string
        
        struct C(B) x:int
        
        struct AAbbbc
            a:int
            b: string
        
        if x < 5
            y = 80
        for i <- [1..5]
        for i=0; i < 5; i += 1
        
        res <- (1,2)
        \ x -> x
        \ x, y -> x + y - foo()
        (a, b, c) -> a + b + c
        @debug 123 Hello debug )
        if 1 /:  if 123 /: 2
        while a < 5
        match n
        if x
        return 14
        return (a + b)
        import mod
        import mod > *
        import mymodule > foo f1, bar f2
        enum Abc
        1, 2, 3
        aa; bbb ;c
        a:int
        foo:function
        f00 * bar $ arg
        foo * bar~>(1)(2) $ arg
        a :: int
        ab: A|B = null
        ff = x -> x + 2
        
        ## match cases
        
        match nn$/N  a :: int
        match nn$/N  a :: int|float
        match nn$/N  1 | 2 | 3
        match nn$/N  () | {}
        match nn$/N  :: A
        match nn$/N  A{}
        
        
        #= bugs
        
        '''
        data = norm(data[1:]).splitlines()
        for src in data:
            if '' == src.strip():
                continue
            src = src.replace('$/N', '\n')

            tlines = splitLexems(src)
            # print('', [[(l.val, Lt.name(l.ltype)) for l in n.lexems] for n in tlines])
            clines:CLine = elemStream(tlines)
            # print('', [c for c in clines])
            try:
                expTree = lex2tree(clines)
            except LangError as ex:
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n!! Error LangError:', ex.msg)
                self.fail()
                # raise ex
            except Exception as ex:
                # print('`=`=`=`=`=`=`=`\n!!Error Exception', ex.args)
                self.fail()
                # raise ex

    # def test_interpret_profile(self):
    #     ''' '''
    #     prof.runctx('self.interpret_base_cases()', globals(), locals())
        

    def _test_base_lang_cases(self):
        self.interpret_base_cases()

    def _test_code3(self):
        ''' '''
        code = r'''
        
        res = []
        
        x = 1
        y = 0
        if x > 5
            res <- 2
        else if x > 0
            res <- 3
        else
            res <- 7
        
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

