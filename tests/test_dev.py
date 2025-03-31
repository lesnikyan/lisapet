

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from eval import rootContext
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tree import *
from nodes.structs import *
import pdb


class A:
    pass

class B:
    pass

class C(A,B):
    pass


class TestDev(TestCase):
    
    '''
    TODO:
    test assignment and read 
    global var and local block
    local var and function-block
    var <- val
    var <- var
    var <- array
    array <- var
    dict of items str : array
    array of dicts
    
    '''

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

    def test_struct_inline(self):
        # code='''
        # struct User
        #     name
        #     age
        #     sex
        #     phone
        # '''
        code='''
        struct User name, age, sex, phone
        user = User{name:'Catod', age:25, sex:male, phone:'123-45-67'}
        print('phone:', user.phone)
        '''
        tt = '''
        user = User{name:'Catod', sex:male}
        user = User{'Catod', 25, male, '123-45-67'}
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rtype = ctx.getType('User')
        print('# TT >>>', rtype)

    def _test_struct_field_type(self):
        type1 = StructDef('Test1')
        fields = [
            Var(None, 'amount', TypeInt),
            Var(None, 'weight', TypeFloat),
            Var(None, 'title', TypeString)
        ]
        for ff in fields:
            type1.add(ff)
        inst = StructInstance('varName', type1)
        inst.set('amount', value(12, TypeInt))
        print('## T >>> ', inst.get('amount'))
        # inst.set('amount', value('12', TypeString))
        # print('## T >>> ', inst.get('amount'))

    def _test_type_nums(self):
        code = '''
        a: int = 5
        b: float = 10
        c = b / a
        print(c, type(c))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        res = ctx.get('res').get()
        print('##################t-IF1:', )
        self.assertEqual(res, 45)

if __name__ == '__main__':
    main()
