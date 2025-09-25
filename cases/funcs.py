
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
from cases.utils import OperSplitter


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
            dprint('--------------- >>>>>>>>>>>>>>', elemStr(ees))
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

class CaseLambda(CaseFuncDef):
    ''' args -> expr '''
    
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 4:
            return False

        main = OperSplitter().mainOper(elems)
        dprint('CaseLamb, main=', main, ' len_elems:', len(elems))
        dprint('CaseLambda elems[main]', elems[main].text, main)
        return isLex(elems[main], Lt.oper, '->')

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' func name (arg, arg, arg, ..) 
        method:
            func u:User setName(name:string)
        '''
        idx = OperSplitter().mainOper(elems)
        args = elems[:idx]
        if CaseBrackets().match(args):
            args = args[1:-1]
        body = elems[idx+1:]
        exp = FuncDefExpr(None) # lambda has no name
        return exp, [args, body]

    def setSub(self, base:FuncDefExpr, subs:Expression|list[Expression])->Expression:
        dprint('CaseLambda. setSub', base,  ' \\ ', subs)
        args, body = subs
        if isinstance(args, SequenceExpr):
            for arg in args.subs:
                base.addArg(arg)
        else:
            base.addArg(args)
        
        base.add(body)
        return base


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
        dprint('CaseMathodDef split', exp)
        return exp, subs

    def setSub(self, base:MethodDefExpr, subs:Expression|list[Expression])->Expression:
        inst = subs[0]
        args = []
        # dprint('CaseMathodDef seSub1', base, subs)
        if len(subs) > 1:
            args = subs[1:]
        dprint('CaseMathodDef seSub2', base, inst, args)
        base.setInst(inst)
        for exp in args:
            base.addArg(exp)
        return base



class CaseFunCall(SubCase):
    ''' foo(agrs)
        {expr}(args)'''

    # def match1(self, elems:list[Elem]) -> bool:
    #     ''' simple cases:
    #         foo(), foo(a, b, c), foo(bar(baz(a,b,c-d+123)))
    #         spec words  should not be here (for, if, func, match, return..)
    #         TODO: complex cases:
    #         (lambda-or-func)(), cont[key](), (any-expr)()
    #     '''
    #     if len(elems) < 3:
    #         return False
    #     if not isLex(elems[-1], Lt.oper, ')'):
    #         return False
    #     if elems[0].type != Lt.word: # incorrect for (function)()
    #         return False
    #     if not isLex(elems[1], Lt.oper, '('):
    #         return False
    #     if elems[0].type == Lt.word and elems[0].text in KEYWORDS:
    #         return False
    #     # TODO: use word(any-with-brackets) pattern
    #     endInd = afterNameBr(elems)
    #     if endInd != -1:
    #         return False
    #     return True

    def match(self, elems:list[Elem]) -> bool:
        ''' simple cases:
            foo(), foo(a, b, c), foo(bar(baz(a,b,c-d+123)))
            spec words  should not be here (for, if, func, match, return..)
            TODO: complex cases:
            foo()(), (lambda-or-func)(), cont[key]()
            name()[]()[]() () # multiple brackets after name
            (expr)[]()[]()[] # multiple brackets after brackets
            [x -> expr][0](arg) # lambda in list
        '''
        # print('CaseFunCall.matchNew ::: ', ''.join([n.text for n in elems]))
        if len(elems) < 3:
            return False
        if not isLex(elems[-1], Lt.oper, ')'):
            return False
        if elems[0].type == Lt.word and elems[0].text in KEYWORDS:
            return False
        # TODO: use word(any-with-brackets) pattern
        
        # print('FuncCallMatch ---------1----------')
        if not isGetValExpr(elems):
            return False
        
        # print('FuncCallMatch ---------2----------')
        opInd = findLastBrackets(elems)

        if opInd < 1:
            # means only brackets, no collection var before
            return False
        if not isLex(elems[opInd], Lt.oper, '('):
            return False
        # print('FuncCallMatch ---------3----------')
        
        # endInd = afterNameBr(elems)
        # if endInd != -1:
        #     return False
        return True
        
        # if elems[1].type != Lt.oper or elems[-1].type != Lt.oper or elems[1].text != '(' or elems[-1].text != ')':
        #     return False
    
    # def split1(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
    #     ''' '''
    #     # 1. func name, in next phase: method call: inst.foo() ? separated case for objects with members: obj.field, obj.method()
    #     # 2. arg-expressions
    #     src = elemStr(elems)
    #     name = elems[0].text
    #     # argSrc = elems[2:-1]
    #     sub = elems[2:-1]
    #     cs = CaseCommas()
    #     subs = [sub] # one expression inside by default
    #     if cs.match(sub):
    #         _, subs = cs.split(sub)
    #         # TODO: if function not just defined name: (lambda)(), funcs[key]()
    #         # func should be an expression which returns function object
    #     exp = FuncCallExpr(name, src)
    #     return exp, subs

    # def setSub1(self, base:FuncCallExpr, subs:Expression|list[Expression])->Expression: 
    #     ''' base - FuncCallExpr, subs - argVal expressions '''
    #     for exp in subs:
    #         dprint('FN Call sub:', exp)
    #         base.addArgExpr(exp)
    #     return base
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # 1. func name, in next phase: method call: inst.foo() ? separated case for objects with members: obj.field, obj.method()
        # 2. arg-expressions

        src = elemStr(elems)
        opInd = findLastBrackets(elems)
        argEl = elems[opInd+1 : -1]
        args = [argEl] # one expression inside by default
        valExpr = elems[:opInd]
        cs = CaseCommas()
        if cs.match(argEl):
            _, args = cs.split(argEl)
        exp = FuncCallExpr(elemStr(valExpr), src)
        # print('FCall.split1', valExpr, args)
        subs = [valExpr] + args
        # print('FCall.split2', subs)
        return exp, subs

    def setSub(self, base:FuncCallExpr, subs:Expression|list[Expression])->Expression: 
        ''' base - FuncCallExpr, subs - argVal expressions '''
        fexpr = subs[0]
        args = [n for n in subs[1:] if not isinstance(n, NothingExpr)]
        # print('FCall.setSub1', subs)
        # print('FCall.setSub2',fexpr, args)
        base.setFuncExpr(fexpr)
        for exp in args:
            # print('FCall add arg:', exp)
            base.addArgExpr(exp)
        return base
