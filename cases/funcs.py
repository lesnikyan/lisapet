
'''
Functions cases
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from nodes.tnodes import *
from nodes.func_expr import *
from cases.tcases import *
from cases.oper import *
from cases.structs import MethodDefExpr, MethodCallExpr


class CaseFuncDef(BlockCase, SubCase):
    ''' func foo(arg-expressions over comma) '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 4:
            return False
        if isLex(elems[0], Lt.word, 'func') and isLex(elems[2], Lt.oper, '('):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' func name (arg, arg, arg, ..) 
        method:
            func u:User setName(name:string)
        '''
        
        fname = elems[1].text
        exp = FuncDefExpr(fname)
        subs = self.splitArgs(elems[3:-1])
        subs = [ees for ees in subs if len(ees) > 0]
        for ees in subs:
            print('--------------- >>>>>>>>>>>>>>', elemStr(ees))
        return exp, subs

    def splitArgs(self, elems):
        cs = CaseCommas()
        subs = [elems]
        if cs.match(elems):
            _, subs = cs.split(elems)
        return subs
        

    def setSub(self, base:FuncDefExpr, subs:Expression|list[Expression])->Expression:
        for exp in subs:
            base.addArg(exp)


class CaseMathodDef(CaseFuncDef):
    ''' func inst:Type foo(arg-expressions over comma) '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 7:
            return False
        if not isLex(elems[0], Lt.word, 'func'):
            return False
        cc = CaseColon()
        return cc.match(elems[1:4])

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        argSubs = self.splitArgs(elems[6:-1])
        argSubs = [ees for ees in argSubs if len(ees) > 0]
        # return exp, subs
        instSub = elems[1:4]
        subs = [instSub] + argSubs
        fname = elems[4].text
        exp = MethodDefExpr(fname)
        print('CaseMathodDef split', exp)
        return exp, subs

    def setSub(self, base:MethodDefExpr, subs:Expression|list[Expression])->Expression:
        inst = subs[0]
        args = []
        # print('CaseMathodDef seSub1', base, subs)
        if len(subs) > 1:
            args = subs[1:]
        print('CaseMathodDef seSub2', base, inst, args)
        base.setInst(inst)
        for exp in args:
            base.addArg(exp)
        return base



class CaseFunCall(SubCase):
    ''' foo(agrs)'''

    def match(self, elems:list[Elem]) -> bool:
        ''' foo(), foo(a, b, c), foo(bar(baz(a,b,c-d+123)))
            spec words  sould not be here (for, if, func, match, return..)
        '''
        if len(elems) < 3:
            return False
        if elems[0].type != Lt.word:
            return False
        if not isLex(elems[1], Lt.oper, '('):
            return False
        # TODO: use word(any-with-brackets) pattern
        endInd = afterNameBr(elems)
        if endInd != -1:
            return False
        return True
        
        # if elems[1].type != Lt.oper or elems[-1].type != Lt.oper or elems[1].text != '(' or elems[-1].text != ')':
        #     return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # 1. func name, in next phase: method call: inst.foo() ? separated case for objects with members: obj.field, obj.method()
        # 2. arg-expressions
        src = elemStr(elems)
        name = elems[0].text
        # argSrc = elems[2:-1]
        sub = elems[2:-1]
        cs = CaseCommas()
        subs = [sub] # one expression inside by default
        if cs.match(sub):
            _, subs = cs.split(sub)
        exp = FuncCallExpr(name, src)
        return exp, subs

    def setSub(self, base:FuncCallExpr, subs:Expression|list[Expression])->Expression: 
        ''' base - FuncCallExpr, subs - argVal expressions '''
        for exp in subs:
            base.addArgExpr(exp)
        return base

class CaseReturn(SubCase):
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'return'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' We have to 
        1. store result of next after return expr
        2. stop execution next lines'''
        subs = [elems[1:]]
        exp = ReturnExpr()
        return exp, subs
    
    def setSub(self, base:ReturnExpr, subs:list[Expression])->Expression:
        base.setSub(subs[0])
        return base

