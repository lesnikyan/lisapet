

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

    def _test_import_module_struct(self):
        stMod = self.loadStructs()
        code = '''
        
        import tstructs.*
        # pr = Pair{a:10, b:200}
        # res = [pr.foo(), ]
        #pr.sum(), pr.mult()
        print('res:', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        curMod = lex2tree(clines)
        
        rootCtx = moduleContext()
        rootCtx.loadModule(stMod)
        curMod.do(rootCtx)

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

        rootCtx = moduleContext()
        rootCtx.loadModule(funMod)
        curMod.do(rootCtx)

        f1 = rootCtx.get('f1')
        f2 = rootCtx.get('f2')
        f3 = rootCtx.get('f3')
        print('#TT 1>> ', f1, f2, f3)
        res = rootCtx.get('res').get()
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

        rootCtx = moduleContext()
        rootCtx.loadModule(funMod)
        curMod.do(rootCtx)

        f1 = rootCtx.get('foo')
        f2 = rootCtx.get('sum')
        f3 = rootCtx.get('mult')
        print('#TT 1>> ', f1, f2, f3)
        res = rootCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([123, 210, 340], res.vals())

    def test_import_module_func(self):
        
        # imported part
        # ctxFuncs = moduleContext()
        funMod = self.importFuncs()
        # funMod.do(ctxFuncs)
        
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
        rootCtx = moduleContext()
        rootCtx.loadModule(funMod)
        # rootCtx.loadModule('tfuncs', ctxFuncs)
        curMod.do(rootCtx)
        f1 = rootCtx.get('foo')
        f2 = rootCtx.get('sum')
        f3 = rootCtx.get('mult')
        print('#TT 1>> ', f1, f2, f3)
        res = rootCtx.get('res').get()
        print('#TT 2>> ', res.vals())
        self.assertEqual([123, 210, 340], res.vals())
        



if __name__ == '__main__':
    main()
