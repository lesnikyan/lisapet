

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


class TestStruts(TestCase):



    def test_struct_inheritance(self):
        ''' '''
        code = r'''
        struct Aaaa a1: int, a2: string
        
        func a:Aaaa f1(x:int, y:int)
            a.a1 = x + y
        
        struct Cccc c:int
        
        struct B(Aaaa, Cccc) b:int
        
        b1 = B{b:1, a1:12, a2:'B-aa'}
        b2 = B{b:2}
        
        b2.f1(3, 4)
        
        b2.a1 += 10
        
        res = b2.a1
        res2 = b1.a2
        print('res = ', res, res2)
        '''
        _='''
        
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        # ctx.print()
        rvar = ctx.get('res')
        self.assertEqual(17, rvar.getVal())

    def test_structType_in_func(self):
        ''' test if type defined in context above is accessible in function '''
        code = '''
        struct Type1
            name: string
            id: int

        func tip:Type1 setName(name:string)
            tip.name = name

        func tip:Type1 getName()
            tip.name

        func testType1()
            tp1 = Type1 {name:'noname', id: 1}
            tp1.setName('New-Name')
            print('tp1 name:', tp1.getName())

        testType1()
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_method_typed_args(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        
        struct MyType name: string
        
        func st: MyType foo(nn: int, ff: float, arg4 )
            print('arg4:', arg4)
            div = ' ' * nn
            st.name + div + '/'
        
        dd = {'a':1}
        
        myt = MyType{name: 'Grrr'}
        myt.name = 'Rrrr'
        
        print('p>>', myt.foo(4, 0.1, '4444'))
        '''
        tt = '''
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_struct_method_call(self):
        ''' struct method definition  '''
        code = '''
        
        func xprint(arg)
            print('<x>', arg, '<x>')
        
        struct User
            name: string 

        func u:User setName(name)
            print('x@1', name)
            print('x@2', u.name)
            u.name = name
            print('x@3', u.name)
        user = User{name:'Markos'}
        user.setName('Lukas')
        xprint(user.name)
        '''
        tt = '''

        # Contexts().types['User'].__typeMethods['setName'] = Function('User@setName')

        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        usr = ctx.get('user').get()
        print('#tt user.name:', usr.get('name').get())
        self.assertEqual('Lukas', usr.get('name').get())

    def test_struct_method_definition(self):
        ''' struct method definition  '''
        code = '''
        struct User
            name: string 

        func u:User setName(name:string)
            u.name = name

        user = User{name:'Markus'}
        '''
        tt = '''
        '''
        # Contexts().types['User'].__typeMethods['setName'] = Function('User@setName')
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

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
        dprint(atype, btype)

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
            dprint(elemStr(elems), '>>', ind, '>>>', '  ', elems[ind].text)
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

        @debug 123321
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
        b0 = ctx.get('books').get().elems[0]
        dprint('#tt b0:', b0.get('prod').get('price').get())
        self.assertEqual(11.0, b0.get('prod').get('price').get())

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
        c = ctx.get('c').get()
        dprint('#tt b0:', c.get('cbb').get())
        self.assertEqual('c-val2', c.get('cbb').get())

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
        dprint('# TT >>>', rtype)

    def test_struct_field_type(self):
        type1 = StructDef('Test1')
        fields = [
            Var('amount', TypeInt()),
            Var('weight', TypeFloat()),
            Var('title', TypeString())
        ]
        for ff in fields:
            type1.add(ff)
        inst = StructInstance(type1)
        inst.set('amount', Val(12, TypeInt()))
        dprint('## T >>> ', inst.get('amount'))
        # inst.set('amount', value('12', TypeString))
        # dprint('## T >>> ', inst.get('amount'))

if __name__ == '__main__':
    main()
