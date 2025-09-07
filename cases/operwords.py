'''
Operators defined as text-word:
return
break
continue

'''

from lang import *
from vars import *
from vals import isLex

from cases.tcases import *


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



class CaseBreak(SubCase):
    ''' break '''
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'break'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' ''' 
        # subs = [elems[1:]]
        exp = BreakExpr()
        return exp, []
    
    def setSub(self, base:BreakExpr, subs:list[Expression])->Expression:
        # base.setSub(subs[0])
        return base


class CaseContinue(SubCase):
    ''' continue '''
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'continue'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ContinueExpr()
        return exp, []
    
    def setSub(self, base:ContinueExpr, subs:list[Expression])->Expression:
        # base.setSub(subs[0])
        return base
