

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
    def __init__(self):
        self.field = '111'

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

    def _test_struct_block(self):
        code='''
        struct User
            name
            age
            sex
            phone
        user = User{name:'Catod', age:25, sex:male, phone:'123-45-67'}
        print('phone:', user.phone)
        '''
        tt = '''
        user = User
            name:'Catod'
            age:25
            sex:male
            phone:'123-45-67'
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_struct_field_full(self):
        ''' full test of obj.member cases '''
        code='''
        obj.member
        obj.member.member.member
        array[expr].member
        array[expr].member[key].member
        array[expr.member].member
        array[expr].member
        foo(args).member
        obj.fmember()
        obj.fmember(args)
        foo().bar().baz().member
        foo().bar().baz().member.member
        foo().bar().baz().member.method(args)
        array[foo()].member[key].method()
        '''
        code = norm(code[1:])
    
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

    def _test_struct_block(self):
        code='''
        struct User
            name
            age
            sex
            phone
        user = User{name:'Catod', age:25, sex:male, phone:'123-45-67'}
        print('phone:', user.phone)
        '''
        tt = '''
        user = User
            name:'Catod'
            age:25
            sex:male
            phone:'123-45-67'
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

if __name__ == '__main__':
    main()
