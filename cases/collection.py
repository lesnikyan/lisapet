'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *

from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.datanodes import *


class CaseArray(SubCase):
    ''' [num, word, expr] '''

    def match(self, elems:list[Elem]) -> bool:
        # trivial check
        # TODO: add check for complex cases like [] + []
        if isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ListExpr()
        sub = elems[1:-1]
        cs = CaseCommas()
        subs = [sub]
        if cs.match(sub):
            _, subs = cs.split(sub)
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        print('CaseArray.setSub: ', base, subs)
        for exp in subs:
            base.add(exp)
        return base

class CaseCollectElem(SubCase):
    ''' 
    case array[index-expr]
    case dict[key-expr]
    usage:
    get: a = arr[expr]; 
    set: arr[expr] = expr
    varName_Expression [ indexVal_Expression ]
    [] - access to array operator
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''
        simplest: varName[indexVar|intVal]
        elems[0]: varName, funcName + (expr), 
        more complex: obj.field, obj.method(expr)
        '''
        prels('CaseCollectElem.match1', elems)
        opIndex = afterNameBr(elems)
        oper = elems[opIndex]
        print('CaseCollectElem, oper =', oper.text, 'index=', opIndex)
        if opIndex == -1 and isLex(elems[-1], Lt.oper, ']'):
            # case: var[key]
            return True
        
        if len(elems) < 4:
            return False
        # assign to no-key case var[] = 123
        
        # simple case: varName [ any ]
        if len(elems) == 4 and elems[0].type == Lt.word and isLex(elems[1], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'):
            # check internal brackets to avoide a[]...b[]
            return True
        # TODO: match complex cases: var.meth(arg, arg, arg)[foo(var.field + smth) - arr[index + var]]
        
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        '''
        execution plan:
        1. get Var in context
        2. eval key|index expr
        3. get val from collection by index|key
        '''
        varElems = []
        keyElems = []
        for ee in elems:
            if isLex(ee, Lt.oper, '['):
                keyElems = elems[len(varElems)+1: -1]
                break
            varElems.append(ee)
        exp = CollectElemExpr()
        return exp, [varElems, keyElems]
            
    def setSub(self, base:CollectElemExpr, subs:Expression|list[Expression])->Expression:
        base.setVarExpr(subs[0])
        base.setKeyExpr(subs[1])
        return base


class CaseDictLine(SubCase):
    ''' {expr:expr, ...} - here single line case
        multi-line declaration with { } - another case
        multiline declaration as val = dict // - another.. not sure 
    '''

    def match(self, elems:list[Elem]) -> bool:
        print('CaseDictLine.match')
        if not isBrPair(elems, '{','}'):
            return False
        
        if len(elems) == 2:
            # empty dict {}
            print('case-dict empty')
            return True

        ind = bracketsPart(elems)
        print('case-dict ind', ind)
        if ind != -1:
            return False

        # check CaseCommas into { }
        subel = elems[1:-1]
        cs = CaseCommas()
        cc = CaseColon()
        if not cs.match(subel):
            # guess 1 item, check colon-separeted seq
            print('CaseDictLine.match2')
            return self.checkValidSub(subel, cc)
        print('CaseDictLine.match3')
        _, parts = cs.split(subel)
        for pp in parts:
            print('CaseDictLine.match4:', elemStr(pp))
            if not self.checkValidSub(pp, cc):
                print('CaseDictLine.match5 not valid')
                return False
        return True
        # return False

    def checkValidSub(self, elems, cc:CaseColon):
        if not cc.match(elems):
            return False
        _, pair = cc.split(elems)
        print('CD.checkValidSub', len(pair), [elemStr(n) for n in pair])
        return len(pair) ==2
            # # something like {a:b:c}
            # return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = DictExpr()
        sub = elems[1:-1]
        cs = CaseCommas()
        cc = CaseColon()
        subs = [sub] # 1 elem
        if cs.match(sub):
            _, subs = cs.split(sub)
            # for pair in subs:
            #     if not cc.match(pair):
            #         raise InerpretErr('Error while split sub-dict expression: `%s` ' % elemStr(pair))
            #     psub = cc.split(pair)
        return exp, subs

    def setSub(self, base:DictExpr, subs:Expression|list[Expression])->Expression:
        print('CaseDict.setSub: ', base, subs)
        for exp in subs:
            base.add(exp)
        return base



class CaseDictBlock(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        '''
        dict
        from varName = dict
        '''
        # print('CaseDictBlock.match')
        if len(elems) != 1:
            return False
        return isLex(elems[0], Lt.word, 'dict')
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        return DictConstr(), []

    def setSub(self, base:DictConstr, subs:Expression|list[Expression])->Expression:
        print('CaseDict.setSub empty: ', base, subs)



