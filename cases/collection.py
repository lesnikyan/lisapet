'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *

from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.datanodes import *




def keyBorders(elems:list[Elem]):
    open, close = 0, 0
    # i = -1
    lel = len(elems)
    for i in range(0, lel, 1):
        ee = elems[i]
        if isLex(ee, Lt.oper, '['):
            open = i
            break
    for i in range(lel-1, -1, -1):
        ee = elems[i]
        if isLex(ee, Lt.oper, ']'):
            close = i
            break
    return open, close


class CaseTuple(SubCase):
    ''' (a, b, c) '''

    def match(self, elems:list[Elem]) -> bool:
        # trivial check
        if not (isLex(elems[0], Lt.oper, '(') and isLex(elems[-1], Lt.oper, ')')):
            return False
        cs = CaseCommas()
        return cs.match(elems[1:-1])

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[1:-1]
        cs = CaseCommas()
        subs = [sub]
        if cs.match(sub):
            _, subs = cs.split(sub)
        exp = TupleExpr()
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        print('CaseTuple.setSub: ', base, subs)
        for exp in subs:
            base.add(exp)
        return base

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


class CaseListBlock(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        '''
        list
        varName = list
        '''
        if len(elems) != 1:
            return False
        return isLex(elems[0], Lt.word, 'list')
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        return ListConstr(), []

    def setSub(self, base:ListConstr, subs:Expression|list[Expression])->Expression:
        print('ListConstr.setSub empty: ', base, subs)


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

        if not self.matchOuter(elems):
            return False
        
        opInd = findLastBrackets(elems)
        if opInd < 1:
            # means only brackets, no collection var before
            return False

        # prels('CaseCollectElem match1:', elems, opInd)
        # prels('CaseCollectElem match2:', elems[opInd+1 : -1])
        # filtering slice
        hasColon = CaseColon().match(elems[opInd+1 : -1])
        # print('CaseCollectElem hasColon', hasColon)
        return not hasColon

    def matchOuter(self, elems:list[Elem]):
        ''' iaf expr is varExpr + [smth] '''
        if len(elems) < 4:
            return False
        return endsWithBrackets(elems, '[]')

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        '''
        execution plan:
        1. get Var in context
        2. eval key|index expr
        3. get val from collection by index|key
        '''

        exp = CollectElemExpr()
        opInd = findLastBrackets(elems)
        varElems = elems[:opInd] # (array)[key-expr]
        keyElems = elems[opInd+1 : -1] # array[(key-expr)]
        return exp, [varElems, keyElems]

    def setSub(self, base:CollectElemExpr, subs:Expression|list[Expression])->Expression:
        base.setVarExpr(subs[0])
        base.setKeyExpr(subs[1])
        return base


class CaseSlice(SubCase):

    def match(self, elems:list[Elem]) -> bool:        
        ''' arr.expr[start-expr : end-expr] 
            TODO: super[key-expr][start : end]
        '''
        if not CaseCollectElem().matchOuter(elems):
            return False
        
        opInd = findLastBrackets(elems)

        cc = CaseColon()
        subPart = elems[opInd+1 : -1]
        hasColon = cc.match(subPart)
        _, ccParts = cc.split(subPart)
        print('CaseSlice match', hasColon, ccParts, len(ccParts))
        return hasColon and (len(ccParts) == 2 or isLex(subPart[-1], Lt.oper, ':'))


    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        opInd = findLastBrackets(elems)
        subPart = elems[opInd+1 : -1]
        cc = CaseColon()
        _, keys = cc.split(subPart)
        varexp = elems[:opInd]
        exp = SliceExpr()
        return exp, [varexp]+ keys

    def setSub(self, base:CollectElemExpr, subs:Expression|list[Expression])->Expression:
        print('CaseSlice setSub', base, subs)
        base.setVarExpr(subs[0])
        base.setKeysExpr(subs[1], subs[2])
        return base


class CaseDictLine(SubCase):
    ''' {expr:expr, ...} - here single line case
        multi-line declaration with { } - another case
        multiline declaration as val = dict // - another.. not sure 
    '''

    def match(self, elems:list[Elem]) -> bool:
        if not isBrPair(elems, '{','}'):
            return False
        
        if len(elems) == 2:
            print('case-dict empty')
            return True

        ind = bracketsPart(elems)
        # print('case-dict ind', ind)
        if ind != -1:
            return False

        # check CaseCommas into { }
        subel = elems[1:-1]
        cs = CaseCommas()
        cc = CaseColon()
        if not cs.match(subel):
            # guess 1 item, check colon-separeted seq
            return self.checkValidSub(subel, cc)
        _, parts = cs.split(subel)
        for pp in parts:
            if not self.checkValidSub(pp, cc):
                return False
        return True
        # return False

    def checkValidSub(self, elems, cc:CaseColon):
        if not cc.match(elems):
            return False
        _, pair = cc.split(elems)
        return len(pair) ==2
            # # something like {a:b:c}
            # return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = DictExpr()
        sub = elems[1:-1]
        cs = CaseCommas()
        # cc = CaseColon()
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
        print('CaseDictBlock.setSub empty: ', base, subs)



