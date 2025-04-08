'''
Cases: 

struct Named inline

struct Named multiline

struct constructor

struct anonymous

struct methods

functions for structs:
fields(instance) : [str]
methods(instans) : []
isnull(var)

'''

from vars import *
from cases.tcases import *
from cases.collection import CaseDictLine
from nodes.expression import *
from nodes.structs import *


class CaseStructDef(SubCase):
    ''' 
    Testins cases with structs and struct members

    struct TypeName field1, field2, field3

    struct TypeName
        field1
        field2

    struct TypeName field1: type1, field2:type2, field3: type3
    
    structVar = TypeName {arg:val, arg:val}
    '''

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
        usr = ctx.get('user')
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

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 3:
            return False
        if isLex(elems[0], Lt.word, 'struct') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        typeName = elems[1].text
        sub = elems[2:]
        exp = StructDefExpr(typeName)
        subs = []
        if sub:
            subs = [sub]
        cs = CaseCommas()
        if cs.match(sub):
            _, subs = cs.split(sub)
        InterpretContext.get().addStruct(typeName)
        return exp, subs

    def setSub(self, base:StructDefExpr, subs:list[Expression])->Expression:
        print('', base, subs)
        for exp in subs:
            base.add(exp)
        return base


class CaseStructBlockDef(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        '''
        struct TypeName
            ...
        '''
        # print('CaseDictBlock.match')
        if len(elems) != 2:
            return False
        return isLex(elems[0], Lt.word, 'struct') and elems[1].type == Lt.word

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp, subs = CaseStructDef().split(elems)
        exp.toBlock()
        return exp, subs

    def setSub(self, base:DictConstr, subs:Expression|list[Expression])->Expression:
        print('CaseDictBlock.setSub empty: ', base, subs)
        return base


class CaseStructConstr(SubCase):
    ''' 
        inline struct creation
        Example:
            varName = TypeName {}
            varName = TypeName {val, val}
            varName = TypeName {field: val, field: val}
        right part: 
            TypeName {field: val, field: val}
    '''
    def match(self, elems:list[Elem]) -> bool:
        '''
        TypeName {dict-like part}
        '''
        el0 = elems[0]
        if el0.type != Lt.word:
            return False
        if len(elems) > 1:
            dc = CaseDictLine()
            return dc.match(elems[1:])
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        typeName = elems[0].text
        sub = elems[2:-1]
        cs = CaseCommas()
        subs = [sub]
        if cs.match(sub):
            _, subs = cs.split(sub)
        return StructConstr(typeName), subs

    def setSub(self, base:StructConstr, subs:Expression|list[Expression])->Expression:
        print('StructConstr.setSub empty: ', base, subs)
        for exp in subs:
            base.add(exp)
        return base


class CaseStructBlockConstr(SubCase):
    ''' 
        inline struct creation
        Example:
            varName = TypeName
                field: val
                field: val
    '''
    # def match(self, elems:list[Elem]) -> bool:
    #     if len(elems) != 1:
    #         return False
    #     return InterpretContext.get().hasStruct(elems[0].text)
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        typeName = elems[0].text
        # if  InterpretContext.get().hasStruct(typeName):
        #     # begin of multiline srtuct constructor
        #     expr 
        # sub = elems[2:-1]
        # cs = CaseCommas()
        # subs = [sub]
        # if cs.match(sub):
        #     _, subs = cs.split(sub)
        return StructConstrBegin(elems[0].text), []

    def setSub(self, base:StructConstr, subs:Expression|list[Expression])->Expression:
        print('StructConstr.setSub empty: ', base, subs)
        # for exp in subs:
        #     base.add(exp)
        # return base


# def checkTypes(elems:list[Elem], exp:list[int]):
#     if len(elems) != len(exp):
#         return False
#     for i in range(len(elems)):
#         if elems[i].type != exp[i]:
#             return False
#     return True


# class CaseStructField(SubCase):
#     def match(self, elems:list[Elem]) -> bool:
#         if len(elems) != 3:
#             return False
#         return checkTypes(elems, [Lt.word, Lt.oper, Lt.word]) and elems[1].text == '.'

#     def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
#         return StructField(), [[elems[0]],[elems[2]]]

#     def setSub(self, base:StructField, subs:Expression|list[Expression])->Expression:
#         print('CaseStructField:', base, subs)
#         # raise EvalErr('')
#         base.set(subs[0], subs[1])
#         return base
        
    