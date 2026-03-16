''' '''



from unittest import TestCase, main

# import lang
# import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
# from vals import numLex
# import context
# from context import Context
from bases.strformat import *
# from nodes.structs import *
from tree import *
# from eval import rootContext, moduleContext

# from cases.utils import *
# from nodes.tnodes import Var
# from objects.func import Function
# from nodes.func_expr import setNativeFunc
# from bases.over_ctx import FuncOverSet
from tests.utils import *
# from libs.regexp import *
# from nodes.func_features import *


# import cProfile as prof
# import pdb


            
class TestInterpretTree(TestCase):
    '''
    ## py -m cProfile -s tottime -m unittest

    '''



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
            
            src = 'match n\n    %s' % src

            tlines = splitLexems(src)
            # print('', [[(l.val, Lt.name(l.ltype)) for l in n.lexems] for n in tlines])
            clines:CLine = elemStream(tlines)
            try:
                expTree:Module = lex2tree(clines)
                MatchExpr, CaseExpr 
                # print('tt1>', expTree.subs[0].cases[0].expect.__class__.__name__)
                self.assertIsInstance(expTree.subs[0].cases[0].expect, MatchingPattern)
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
        a, b, c = 1, 2, 3
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
            if src.startswith('#'):
                continue
            src = src.replace('$/N', '\n')

            tlines = splitLexems(src)
            # print('', [[(l.val, Lt.name(l.ltype)) for l in n.lexems] for n in tlines])
            clines:CLine = elemStream(tlines)
            try:
                expTree = lex2tree(clines)
                # print('tt1>', expTree.subs, src)
                self.assertIsInstance(expTree.subs[0], Expression)
            except LangError as ex:
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n!! Error LangError:', ex.msg)
                self.fail()
                # raise ex
            except Exception as ex:
                # print('`=`=`=`=`=`=`=`\n!!Error Exception', ex.args)
                self.fail()
                # raise ex

    # def _test_interpret_profile(self):
    #     ''' profiling test '''
    #     prof.runctx('self.interpret_base_cases()', globals(), locals())
    

    def test_base_lang_cases(self):
        self.interpret_base_cases()


if __name__ == '__main__':
    main()

