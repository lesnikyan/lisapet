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
    ''' One-line struct definition, fields type = Any
    struct TypeName field1, field2, field3
    struct TypeName
        field1
        field2
    
    struct TypeName field1: type1, field2:type2, field3: type3
    
    structVar = TypeName {arg:val, arg:val}
    '''

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 3:
            return False
        if isLex(elems[0], Lt.word, 'struct') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        typeName = elems[1].text
        # struct B(A,C)
        superNames = []
        subStart = 2
        if len(elems) > 2 and isLex(elems[2], Lt.oper, '('):
            # we have super-struct here
            brInd = firstBrackets(elems)
            brOpen, brClose = brInd
            superPart = elems[brOpen+1: brClose]
            _, spl = CaseCommas().split(superPart)
            superNames = [elemStr(n) for n in spl]
            subStart = brClose+1
        
        sub = elems[subStart:]
        exp = StructDefExpr(typeName, src=elems)
        exp.setSuper(superNames)
        subs = []
        if sub:
            subs = [sub]
        cs = CaseCommas()
        if cs.match(sub):
            _, subs = cs.split(sub)
        InterpretContext.get().addStruct(typeName)
        return exp, subs

    def setSub(self, base:StructDefExpr, subs:list[Expression])->Expression:
        for exp in subs:
            base.add(exp)
        return base


class CaseStructBlockDef(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        '''
        struct TypeName
            ...
        '''
        if len(elems) != 2:
            return False
        return isLex(elems[0], Lt.word, 'struct') and elems[1].type == Lt.word

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp, subs = CaseStructDef().split(elems)
        exp.toBlock()
        return exp, subs

    def setSub(self, base:CaseStructDef, subs:Expression|list[Expression])->Expression:
        return base


class CaseStructConstr(SubCase, SolidCase):
    ''' 
        inline struct creation
        Example:
            varName = TypeName {}
            varName = TypeName {val, val}
            varName = TypeName {field: val, field: val}
        right part: 
            TypeName {field: val, field: val}
    '''
    
    def __init__(self):
        super().__init__()
        self.dc = CaseDictLine()
        self.cc = CaseCommas()
    
    def match(self, elems:list[Elem], ind=None) -> bool:
        '''
        TypeName {dict-like args}
        module.Typename{args}
        future anonimous str:
        _{args}
        '''
        # prels('Struct{} match', elems, show=1)
        el0 = elems[0]
        if el0.type != Lt.word:
            return False
        if len(elems) < 2:
            return False
        # dc = CaseDictLine()
        # get curvy brackets part
        # be sure that case already checked as Solid expr
        ok, pos = True, ind
        if ind is None:
            ok, pos = isSolidExpr(elems, getLast=True)
        # print('Str.Match', r)
        # if not isinstance(r, tuple):
        #     return False
        
        # print('lastFound:', ok, pos, 'lenEl:%d' % len(elems), elems[pos].text)
        if not ok or pos > len(elems)-2 or pos < 1 or not isLex(elems[pos], Lt.oper, '{') : 
            return False
        return self.dc.match(elems[pos:])
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        _, pos = isSolidExpr(elems, getLast=True, skipKeywords=True)
        typePart = elems[:pos]
        argPart = elems[pos:]
        argSub = argPart[1:-1]
        # cs = CaseCommas()
        subs = [argSub]
        if len(argSub) > 3 and self.cc.match(argSub):
            _, subs = self.cc.split(argSub)
        return StructConstr(), [typePart] + subs

    def setSub(self, base:StructConstr, subs:Expression|list[Expression])->Expression:
        # print('StructConstr.setSub empty: ', base, subs)
        base.setObj(subs[0])
        args = subs[1:]
        if args:
            for exp in subs[1:]:
                if isinstance(exp, NothingExpr):
                    continue
                base.add(exp)
        return base




class CaseEnum(SubCase):
    '''
    enum Name a, b, c
    enum Name a=1, b, c
    enum Name
        a = 10,
        b,
        c
    '''

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 2:
            return False
        if isLex(elems[0], Lt.word, 'enum') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ename = elems[1].text
        subStart = 2
        
        sub = elems[subStart:]
        # print('enum items: {=%s=}'% elemStr(sub))
        exp = EnumDef(ename, src=elems)
        subs = []
        if sub:
            subs = [sub]
        cs = CaseCommas()
        if cs.match(sub):
            _, subs = cs.split(sub)
        # print('subs:', ['{%s}'% elemStr(s) for s in subs])
        return exp, subs

    def setSub(self, base:EnumDef, subs:list[Expression])->Expression:
        # print('CaseEnum setSub', base, subs)
        for exp in subs:
            base.add(exp)
        return base


# Future cases
class CaseGenConstSet(SubCase):
    ''' set like enum but for other types,
    if enum elem is int value, so enum A a=1; a == 1 >> true
    otherwise this type is strictly related to set-type, and sub val.
    fixet B a=1; a == 1 >> false
    only B.a is equal to B.a
    '''

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 3:
            return False
        if isLex(elems[0], Lt.word, 'enum') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ename = elems[1].text
        # prels('CaseStructDef.split', elems, show=1)
        # struct B(A,C)
        # superNames = []
        subStart = 2
        typeExpr = None
        # If enum has type of elem
        if len(elems) > 3 and isLex(elems[2], Lt.oper, ':'):
            # print('$1:', elems[2].text)
            cv = CaseVar()
            typeElems = elems[3:4]
            if not cv.match(typeElems):
                raise InterpretErr("Incorrect lexem sequence for types Enum definition.")
            typeExpr = cv.expr(typeElems)
            subStart = 4
        
        sub = elems[subStart:]
        #...
    
    
class CaseGrup(SubCase):
    '''
        grup - thing like namespace, or submodule, or final static class
        
        only block syntax
        grup Name
            sub expressions
    '''

    def match(self, elems:list[Elem]) -> bool:
        # print('Grup match', elemStr(elems), len(elems) != 2, isLex(elems[0], Lt.word, 'grup'))
        if len(elems) != 2:
            return False
        return isLex(elems[0], Lt.word, 'grup') and elems[1].type == Lt.word


    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ename = elems[1].text
        exp = GrupNode(ename, src=elems)
        return exp, []

    def setSub(self, base:EnumDef, subs:list[Expression])->Expression:
        # print('CaseEnum setSub', base, subs)
        for exp in subs:
            base.add(exp)
        return base

