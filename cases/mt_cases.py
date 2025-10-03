
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


class MTVar(CaseVar):
    ''' '''    
    

ValCases = [CaseVal(), CaseString()]

class MTVal(CaseVal):
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

class MTString(CaseString):
    ''' matching value
    "abc" | 'aa' | `bb` !-
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        # print('MTString.expr', elemStr(elems))
        subEx = super().expr(elems)
        expr = MCValue(subEx, elems[0].text)
        return expr


class MT_Other(CaseVar_):
    ''' _ !-  '''
    def match(self, elems:list[Elem])-> bool:
        return isLex(elems[0], Lt.word, '_')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MC_Other(src='_')


class MTList(CaseList):
    ''' '''

class MTTuple(CaseTuple):
    ''' '''

class MTDict(CaseDictLine):
    ''' '''

class MTStruct(CaseStructConstr):
    ''' '''

