'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *

from nodes.tnodes import *
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


class CaseTuple(SubCase, SolidCase):
    ''' (a, b, c) '''
    
    def __init__(self):
        super().__init__()
        self.cs = CaseCommas()
        

    def match(self, elems:list[Elem]) -> bool:
        # trivial check
        # TODO: change to usage of OperSplitter
        if not (isLex(elems[0], Lt.oper, '(') and isLex(elems[-1], Lt.oper, ')')):
            return False
        
        # r =  isSolidExpr(elems, getLast=True)
        # if not isinstance(r, tuple):
        #     return False
        # ok, pos = r
        # if not ok or pos != 0:
        #     return False
        # print('Tuple. lastFound:', ok, pos, 'lenEl:%d' % len(elems), elems[pos].text)
        # cs = CaseCommas()
        return self.cs.match(elems[1:-1])

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[1:-1]
        # cs = CaseCommas()
        subs = [sub]
        # if self.cs.match(sub):
        #     _, subs = self.cs.split(sub)
        if len(sub) > 0:
            _, subs = self.cs.split(sub)
        exp = TupleExpr()
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # dprint('CaseTuple.setSub: ', base, subs)
        for exp in subs:
            if isinstance(exp, NothingExpr):
                # empty position after comma
                continue
            base.add(exp)
        return base


_nonListDElims = [';', '..', ':']


class CaseList(SubCase, SolidCase):
    ''' [num, word, expr] '''
    
    def __init__(self):
        super().__init__()
        self.splitter = OperSplitter.getInst()
        self.cs = CaseCommas()
        self.csemic = CaseSemic()

    def match(self, elems:list[Elem]) -> bool:
        lem = len(elems)
        # print('CaseList match ', elemStr(elems), lem)
        if lem < 2:
            return False
        if not (isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']')):
            # print('Not List 1')
            return False
        
        # empty case:
        if lem == 2:
            return True
        if lem == 3:
            return elems[1].type != Lt.oper or elems[1].text != ','
        
        # r =  isSolidExpr(elems, getLast=True)
        # # print('CaseList.of solid:', r)
        # if not isinstance(r, tuple):
        #     return False
        
        # ok, pos = r
        # if not ok or pos != 0:
        #     return False
        
        inElems = elems[1:-1]
        # many items case
        # cs = CaseCommas()
        # smc = CaseSemic()
        # print(' $$$$$$$$$$$$$$$$$$$$ CL.comm', cres)
        
        # if [;]
        # if self.csemic.match(inElems):
        #     return False
        
        cres = self.cs.match(inElems)
        # return cres
        if cres:
            return True

        # expr .. expr - is ok, in setSub wil be fixed
        # print('@', elemStr(elems))
        # TODO: refactor all [subs] cases as top CaseSquareBr, then: List, IterGen, ListGen, Slice
        
        # begn = 1
        # if isLex(elems[1], Lt.oper, ['-','~','!']):
        #     begn = 2
        # return isSolidExpr(elems[begn:-1])
        
        if isHexBytes(inElems):
            # print('CL.isHexBytes')
            return False
        
        # if one elem but complex expression
        opInd = self.splitter.mainOper(inElems, lesser = ',')
        if opInd < 0:
            return True
        # print('CL.opSpl', opInd, inElems[opInd].text)
        return opInd not in _nonListDElims

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ListExpr()
        sub = elems[1:-1]
        # cs = CaseCommas()
        subs = [sub]
        # if self.cs.match(sub):
        #     _, subs = self.cs.split(sub)
        # need to check comma-separated
        if len(sub) > 1:
            _, subs = self.cs.split(sub)
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # print('CaseList.setSub: ', base, subs)
        if len(subs) == 1:
            if isinstance(subs[0], TwoDotsOper):
                # print('$1 ')
                return subs[0].getListGen()
        for exp in subs:
            if isinstance(exp, NothingExpr):
                # empty position after comma
                continue
            base.add(exp)
        return base


class CaseCollectElem(SubCase, SolidCase):
    ''' 
    case array[index-expr]
    case dict[key-expr]
    case tuple[index]
    case getValExpr[key]: foo()[key] ; val[key][key]; obj.field[key]
        obj.foo(args...).field.foo().field[key].foo().field[key][key][key]
        fing pattern: {word () [] . } * + { word () [] } + []
    usage:
    get: a = arr[expr]; 
    set: arr[expr] = expr
    varName_Expression [ indexVal_Expression ]
    [] - access to element of sequence operator
    '''
    
    def __init__(self):
        super().__init__()
        self.ccolon = CaseColon()

    def match(self, elems:list[Elem], ind=None) -> bool:
        '''
        simplest: varName[indexVar|intVal]
        elems[0]: varName, funcName + (expr), 
        more complex: obj.field, obj.method(expr)
        '''
        if not isLex(elems[-1], Lt.oper, ']'):
            # not [] brackets
            return False
        
        if elems[0].type == Lt.num:
            return False
        
        # if ind is not None:
            # print('$2:', ind)
        
        # if not isGetValExpr(elems):
        #     print('$1', elemStr(elems))
        #     return False

        opInd = ind
        if ind is None:
            opInd = findLastBrackets(elems)

        if opInd < 1:
            # means only brackets, no collection var before
            return False

        # prels('CaseCollectElem match1:', elems, opInd)
        # prels('CaseCollectElem match2:', elems[opInd+1 : -1])
        # filtering slice
        hasColon = self.ccolon.match(elems[opInd+1 : -1])
        # dprint('CaseCollectElem hasColon', hasColon)
        return not hasColon

    def matchOuter(self, elems:list[Elem]):
        ''' if expr is varExpr + [smth] '''
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


class CaseSlice(SubCase, SolidCase):
    def __init__(self):
        super().__init__()
        self.ccolon = CaseColon()
        self.lastInd = None

    def match(self, elems:list[Elem], ind=None) -> bool:     
        ''' arr.expr[start-expr : end-expr] 
            TODO: super[key-expr][start : end]
        '''
        # if not CaseCollectElem().matchOuter(elems):
        #     return False
        self.lastInd = None
        
        if len(elems) < 4:
            return False
        
        if not isLex(elems[-1], Lt.oper, ']'):
            # not [] brackets
            return False
        
        opInd = ind
        if ind is None:
            opInd = findLastBrackets(elems)
        self.lastInd = opInd

        # cc = CaseColon()
        subPart = elems[opInd+1 : -1]
        hasColon = self.ccolon.match(subPart)
        if not hasColon:
            return False
        _, ccParts = self.ccolon.split(subPart)
        # dprint('CaseSlice match', hasColon, ccParts, len(ccParts))
        return (len(ccParts) == 2 or isLex(subPart[-1], Lt.oper, ':'))


    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # opInd = findLastBrackets(elems)
        opInd = self.lastInd
        subPart = elems[opInd+1 : -1]
        # cc = CaseColon()
        _, keys = self.ccolon.split(subPart)
        varexp = elems[:opInd]
        exp = SliceExpr()
        return exp, [varexp]+ keys

    def setSub(self, base:CollectElemExpr, subs:Expression|list[Expression])->Expression:
        # dprint('CaseSlice setSub', base, subs)
        base.setVarExpr(subs[0])
        base.setKeysExpr(subs[1], subs[2])
        return base


class CaseDictLine(SubCase, SolidCase):
    ''' {expr:expr, ...} - here single line case
        multi-line declaration with { } - another case
        multiline declaration as val = dict // - another.. not sure 
    '''
    
    def __init__(self):
        super().__init__()
        self.cs = CaseCommas()
        self.cc = CaseColon()

    def match(self, elems:list[Elem]) -> bool:
        if not isBrPair(elems, '{','}'):
            return False
        # prels('dict-c match', elems, show=1)
        if len(elems) == 2:
            # dprint('case-dict empty')
            return True

        # ind = bracketsPart(elems)
        # # print('case-dict ind', ind)
        # if ind != -1:
        #     return False
        
        # r =  isSolidExpr(elems, getLast=True)
        # if not isinstance(r, tuple):
        #     return False
        # ok, pos = r
        # if not ok or pos != 0:
        #     return False

        # check CaseCommas into { }
        subel = elems[1:-1]
        # cs = CaseCommas()
        # cc = CaseColon()
        
        if not self.cs.match(subel):
            # guess 1 item, check colon-separeted seq
            return self.checkValidSub(subel, self.cc)
        
        _, parts = self.cs.split(subel)
        for pp in parts:
            if pp:
                if not self.checkValidSub(pp, self.cc):
                    return False
                
        # parts = [n for n in parts if n]
        # for pp in parts:
        #     if not self.checkValidSub(pp, self.cc):
        #         return False
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
        # prels('dict split', elems, show=1)
        exp = DictExpr()
        sub = elems[1:-1]
        # cs = CaseCommas()
        subs = [sub] # 1 elem
        # if self.cs.match(sub):
        if len(elems) > 5:
            _, subs = self.cs.split(sub)
        return exp, subs

    def setSub(self, base:DictExpr, subs:Expression|list[Expression])->Expression:
        # print('CaseDict.setSub: ', base, subs)
        for exp in subs:
            if isinstance(exp, NothingExpr):
                # empty position after comma
                continue
            base.add(exp)
        return base

