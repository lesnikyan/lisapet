
from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

# from cases.tcases import *
from nodes.control import *
from nodes.match_patterns import *

from cases.tcases import *
from cases.oper import CaseBrackets
from cases.collection import *
from cases.structs import *


'''
Case detection.
! Note: pattern case is not a constructor-expression

# base: simple-val or data-struct

# data-struct: is list, dict, tuple, struct, (Maybe, Tree, etc)

# parse to elems.

# find quantifiers: `_ * ?`



'''


class MTCase(ExpCase):
    ''' case of match pattern '''

ValCases = [CaseVal(), CaseString()]

class MTVal(MTCase, CaseVal):
    ''' matching value
    12 !-
    
    true !-
    null !-
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        subEx = super().expr(elems)
        expr = MCValue(subEx, elems[0].text)
        return expr

class MTString(MTCase, CaseString):
    ''' matching value
    "abc" | 'aa' | `bb` !-
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        # print('MTString.expr', elemStr(elems))
        subEx = super().expr(elems)
        expr = MCValue(subEx, elems[0].text)
        return expr


class MTVar(MTCase,CaseVar):
    ''' '''    
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        vexpr = VarExpr(Var(elems[0].text, TypeAny()))
        ptt = MCSubVar(vexpr)
        return ptt


class MT_Other(MTCase, CaseVar_):
    ''' _ !-  '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '_')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MC_Other(src='_')


class SubElem(MTCase):
    ''' _, ?, * '''

class MTEStar(SubElem):
    ''' * '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '*')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MCStar(src='*')

class MTE_(SubElem):
    ''' _ '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '_')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MC_under(src='_')

class MTEQMark(SubElem):
    ''' ? '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '?')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MCQMark(src='?')

# def listCasePriors():
#     src = ('( ) [ ] { } , | , : ,  `1` ')
    # return [raw.replace('$1$', ',') for raw in src.split(',')]


class MTContr(MTCase):
    ''' pattern-container:
    collections, structs,etc'''
    
    def sub(self)->list[Elem]:
        return True
    
    def setSubs(self, base:MCContr, subs:list[MTCase]):
        for sub in subs:
            base.addSub(sub)

class CommaSeparatedSequence(MTContr):
    ''' {,,} [,,] (,,) '''
    
    def matchEdges(self, elems:list[Elem]):
        pass
    
    def match(self, elems:list[Elem]) -> bool:
        lem = len(elems)
        if lem < 2:
            return False
        if not self.matchEdges(elems):
            return False
        if len(elems) == 2:
            return True
        priors = '( ) [ ] { } , | , : ,  `1` '
        spl = OperSplitter(priors)
        opInd = spl.mainOper(elems)
        if opInd != 0:
            return False
        subElems = elems[1:-1]
        opInd = spl.mainOper(subElems)
        return opInd == -1 or (opInd > 0 and subElems[opInd].text not in ';:')

    def split(self, elems:list[Elem]):
        sub = elems[1:-1]
        cs = CaseCommas()
        subs = []
        if sub:
            subs.append(sub)
        # print('SSq.split:', self.__class__.__name__, '', subs)
        if cs.match(sub):
            _, subs = cs.split(sub)
        return subPatterns(subs)


class MTList(CommaSeparatedSequence):
    '''
    # Simple cases
    [], # empty
    [_], [_,_] # any val, no var assign
    [a], [a,b,c], [a,b,_] # var assign
    [_], [123,_], [_,123] # equal values
    # Complex cases.
    [?], [_,?], [4,?], [?,4] # maybe
    [*], [_,*], [123,*], [123,_,*], # others (any number of elems)
    # Nested
    [[]], [_,[]], [(),_], [{k:v}, {n:m}] # nested collections
    '''

    def matchEdges(self, elems:list[Elem]):
        return (isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'))

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subPtts = self.split(elems)
        # print('MTList.e subPtts:', subPtts)
        exp = MCList()
        self.setSubs(exp, subPtts)
        return exp


class MTTuple(CommaSeparatedSequence):
    ''' (), (1,), (1,2)
        (_), (1,_),
    '''

    def matchEdges(self, elems:list[Elem]):
        return (isLex(elems[0], Lt.oper, '(') and isLex(elems[-1], Lt.oper, ')'))

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subPtts = self.split(elems)
        exp = MCTuple()
        self.setSubs(exp, subPtts)
        return exp


class MTColPair(MTContr, CaseColon):
    ''' * : * '''
    def match(self, elems:list[Elem]) -> bool:
        return False
    

class MTDict(MTContr, CaseDictLine):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        return False

class MTStruct(MTContr, CaseStructConstr):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        return False

class MTFail(MTCase):
    ''' case of incorrect pattern-syntax '''


pMListInnerCases:list[MTCase] = [
    MTVal(), MTVar(), MTString(), MTList(), MTTuple(), MTDict(), MTStruct(), MTE_(), MTEStar(), MTEQMark(),
]


def findCase(elems:list[Elem])->MTCase:
    for cs in pMListInnerCases:
        if cs.match(elems):
            return cs
    return MTFail()

def subPatterns(subs:list[list[Elem]])->list[MTCase]:
    if len(subs) == 0:
        return []
    res = []
    # print('subPatterns#00:', subs)
    for sub in subs:
        ptCase = findCase(sub)
        # print('subPatterns#1:', sub, ptCase)
        # if isinstance(ptCase, MTFail):
            # print(' !! > MP-sub. fail', elemStr(sub))
        ptt = ptCase.expr(sub)
        res.append(ptt)
    
    return res



