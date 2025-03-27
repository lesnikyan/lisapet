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
