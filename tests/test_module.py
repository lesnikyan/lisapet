

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
from eval import rootContext, moduleContext

from strformat import *


from tests.utils import *

import pdb


class TestModule(TestCase):
    ''' Tests of module level '''
    
    # TODO: check and fix  arg:type in imported functions.
    # TODO: fix types in imported structs
    


    def loadCode(self, code, name=''):
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        modEx:Module = lex2tree(clines)
        if name:
            modEx.name = name
        return modEx

    def loadStructs(self):
        code = '''
        # module tstructs
        
        struct Pair
            a: int
            b: int
        
        func p:Pair sum()
            p.a + p.b
        
        func p:Pair mult()
            p.a * p.b
        
        func p:Pair foo()
            123
        
        '''
        return self.loadCode(code, 'tstructs')

    def test_import_module_struct(self):
        stMod = self.loadStructs()
        code = '''
        
        import tstructs > Pair
        pr = Pair{a:10, b:200}
        res = [pr.foo() ]
        b = pr.sum()
        res <- b
        res <- pr.mult()
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        print('## Load module...')
        rCtx.loadModule(stMod)
        print('## Eval code ...')
        curCtx = rCtx.moduleContext()
        curMod.do(curCtx)
        res = curCtx.get('res').get()
        self.assertEqual([123, 210, 2000], res.vals())

    def test_import_module_star_struct(self):
        stMod = self.loadStructs()
        code = '''
        
        import tstructs.*
        pr = Pair{a:10, b:200}
        res = [pr.foo() ]
        b = pr.sum()
        res <- b
        res <- pr.mult()
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        print('## Load module...')
        rCtx.loadModule(stMod)
        print('## Eval code ...')
        curCtx = rCtx.moduleContext()
        curMod.do(curCtx)
        res = curCtx.get('res').get()
        self.assertEqual([123, 210, 2000], res.vals())

    def test_import_module_pure_struct(self):
        ''' Issue in struct method with struct type stored in context of imported module.'''
        stMod = self.loadStructs()
        code = '''
        
        import tstructs
        pr = tstructs.Pair{a:11, b:220}
        res = [pr.foo() ]
        b = pr.sum()
        res <- b
        res <- pr.mult()
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        print('## Load module...')
        rCtx.loadModule(stMod)
        print('## Eval code ...')
        curCtx = rCtx.moduleContext()
        curMod.do(curCtx)
        res = curCtx.get('res').get()
        self.assertEqual([123, 231, 2420], res.vals())

    def importFuncsAgrType(self):
        code = '''
        # module tfuncs
        
        func fill(val: string, num:int)
            return [val; i <- iter(num)]
        
        func sum(a:int , b:int)
            a + b
        
        func mult(a:float, b:float)
            a * b
        
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        modEx:Module = lex2tree(clines)
        modEx.name = 'tfuncs'
        return modEx

    def test_import_module_func_arg_type(self):
        funMod = self.importFuncsAgrType()
    
        code = '''
        
        import tfuncs.*
        a, b, c = 1,2,3
        st = fill('abc', 3)
        b = sum(10, 200)
        c = mult(20, 17)
        # print('#1')
        res = [st, b, c]
        # print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        curCtx = rCtx.moduleContext()
        print('## Load module...')
        rCtx.loadModule(funMod)
        print('## Eval code ...')
        curMod.do(curCtx)
        
        # f1 = curCtx.get('foo')
        # f2 = curCtx.get('sum')
        # f3 = curCtx.get('mult')
        # print('#TT 1>> ', f1, f2, f3)
        res = curCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([['abc', 'abc', 'abc'], 210, 340], res.vals())

    def importFuncs(self):
        code = '''
        # module tfuncs
        
        func foo()
            123
        
        func sum(a , b)
            a + b
        
        func mult(a, b)
            a * b
        
        # res = 1
        # print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        modEx:Module = lex2tree(clines)
        modEx.name = 'tfuncs'
        return modEx

    def test_import_module_func_alias(self):

        funMod = self.importFuncs()
        code = '''
        
        import tfuncs > foo f1, sum f2, mult f3
        
        res = [f1(), f2(10, 200), f3(20, 17)]
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)

        rCtx = rootContext()
        curCtx = rCtx.moduleContext()
        print('## Load module...')
        rCtx.loadModule(funMod)
        print('## Eval code ...')
        curMod.do(curCtx)

        f1 = curCtx.get('f1')
        f2 = curCtx.get('f2')
        f3 = curCtx.get('f3')
        print('#TT 1>> ', f1, f2, f3)
        res = curCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([123, 210, 340], res.vals())

    def test_import_module_func_names(self):

        funMod = self.importFuncs()
        code = '''
        
        import tfuncs > foo, sum, mult
        
        # res = mult(20, 17)
        res = [foo(), sum(10, 200), mult(20, 17)]
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        curCtx = rCtx.moduleContext()
        print('## Load module...')
        rCtx.loadModule(funMod)
        print('## Eval code ...')
        curMod.do(curCtx)

        f1 = curCtx.get('foo')
        f2 = curCtx.get('sum')
        f3 = curCtx.get('mult')
        print('#TT 1>> ', f1, f2, f3)
        res = curCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([123, 210, 340], res.vals())

    def test_import_module_func(self):
        
        # imported part
        funMod = self.importFuncs()
        
        # importing part
        code = '''
        
        import tfuncs.*
        
        res = [foo(), sum(10, 200), mult(20, 17)]
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        curCtx = rCtx.moduleContext()
        print('## Load module...')
        rCtx.loadModule(funMod)
        print('## Eval code ...')
        curMod.do(curCtx)
        
        f1 = curCtx.get('foo')
        f2 = curCtx.get('sum')
        f3 = curCtx.get('mult')
        print('#TT 1>> ', f1, f2, f3)
        res = curCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([123, 210, 340], res.vals())

    def test_import_module(self):
        
        # imported part
        funMod = self.importFuncs()
        
        # importing part
        code = '''
        
        import tfuncs
        
        a = tfuncs.foo()
        b = tfuncs.sum(10, 200)
        c = tfuncs.mult(20, 17)
        res = [a, b, c]
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rCtx = rootContext()
        curCtx = rCtx.moduleContext()
        rCtx.loadModule(funMod)
        curMod.do(curCtx)
        res = curCtx.get('res').get()
        self.assertEqual([123, 210, 340], res.vals())


if __name__ == '__main__':
    main()
