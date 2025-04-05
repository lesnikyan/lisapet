

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


    def test_struct_block_constr(self):
        code='''
        struct Btype title:string
        
        bb = Btype{title:'BBBBB'}

        struct Atype
            name: string
            num: int
            sub: Btype

        aa = Atype
            name:'Vasya'
            num:20
            sub: bb
        print('t-inst: ', aa.name , aa.num , aa.sub.title)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_struct_block(self):
        code='''
        struct Btype
            title: string
            vall: float
        struct Atype
            name: string
            num: int
            sub: Btype
        bb = Btype{title: 'Bim-bom', vall: 11.55}
        aa = Atype{name:'Vasya', num:20, sub: bb}
        print('var user: ', aa.name, aa.num, aa.sub.title, aa.sub.vall)
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

    def test_struct_empty(self):
        code='''
        struct Btype
        struct Atype
            name: string
            num: int
            sub: Btype
        # bb = Btype{title: 'Bim-bom', vall: 11.55}
        aa = Atype{name:'Vasya', num:20, sub:Btype{}}
        print('var user: ', aa.name, aa.num, aa.sub)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        atype = ctx.getType('Atype')
        btype = ctx.getType('Btype')
        print(atype, btype)

    def test_left_assign_arg(self):
        code='''
        obj.member = 11
        obj.member.member.member = 22
        array[expr].member = 33
        array[foo(bar(baz(arg)))].member = 34
        array[expr].member[key].member = 44
        array[expr.member].member = 55
        array[expr].member = 66
        foo(args).member = 77
        obj.fmember().sub = 88
        obj.fmember(args).sub = 99
        foo().bar().baz().member = 100
        foo().bar().baz().member.member = 111
        foo().bar().baz().member.method(args) = 122
        array[foo()].member[key].method() = 133
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:list[CLine] = elemStream(tlines)
        for cline in clines:
            elems = cline.code
            ind = afterLeft(elems)
            print(elemStr(elems), '>>', ind, '>>>', '  ', elems[ind].text)
            self.assertEqual(elems[ind].text, '=')

    def test_deep_nesting_struct2(self):
        '''  '''
        code='''
        struct Product price:float, amount:int
        struct Book title:string, author:string, pages:int, prod:Product
        books = list
            Book{title:'Green  gardens', author:'Bob Stinger', pages:100, prod: Product{price:10., amount:1111}}
            Book{title:'Blue, blue sky', author:'Ani Arabesquin', pages:200, prod: Product{price:20., amount:2222}}
            Book{title:'Silver sword of small town', author:'Arnold Whiteshvartz', pages:300, prod: Product{price:20., amount:3333}}

        books[0].prod.price *= 1.1
        func printBook(book)
            print(book.title, book.author, book.pages, book.prod.price)
        
        printBook(books[0])
        '''
        tt = '''

        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_deep_nesting_struct(self):
        ''' fix dot-operator for flexible access to submembers of struct inner fields.
        implement operator `.` instead of magic `name.name` tepmlate '''
        code='''
        struct A nname:string
        a = A {nname:'AAAAA'}
        @debug field assign
        a.nname = 'AA2222'
        print(a.nname)
        struct B aa:A
        b = B{aa:a}
        struct C bb:B, cbb:string
        struct D cc:C
        c = C{bb:b, cbb:'c-val'}
        d = D{cc:c}
        d.cc.cbb = 'c-val2'
        print(b.aa.nname)
        print(d.cc.bb.aa.nname, d.cc.cbb)
        aaa = [1,2,3,4,5]
        print(len(aaa))
        '''
        tt = '''
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_dot_oper(self):
        code='''
        obj.member
        obj.member.member.member
        '''
        tt = '''
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
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        

    def test_struct_inline_types(self):
        code='''
        struct Sex id:int
        @debug =1
        male = Sex{id:1}
        female= Sex{id:1}
        print(male)
        struct User name:string, age:int, sex:Sex, phone:string
        user = User{name:'Catod', age:25, sex:male, phone:'123-45-67'}
        print('user data:', user.name, user.phone, user.sex)
        '''
        tt = '''
        # print('phone:', user.phone)
        user = User{name:'Catod', sex:male}
        user = User{'Catod', 25, male, '123-45-67'}
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        # rtype = ctx.getType('User')
        # print('# TT >>>', rtype)

    def test_struct_inline(self):
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

    def test_struct_field_type(self):
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
