'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *

# from nodes.tnodes import *
# from nodes.oper_nodes import *
from nodes.control import *
from cases.tcases import *

class CaseMatch(SubCase):
    ''' very specaial case. 
         1. step: match(expr): case 1; case 2: case 3;
         2. case type.
         3. case pattern.
    '''

    def match(self, elems:list[Elem]) -> bool:
        ''' match expr '''
        if len(elems) < 2:
            return False
        if isLex(elems[0], Lt.word, 'match'):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        return MatchExpr(), [elems[1:]]


    def setSub(self, base:MatchExpr, subs:list[Expression])->Expression:
        base.setMatch(subs[0])
        return base


class RawCase:
    ''' case we need do some post-operation '''


class ArrOper(RawCase):
    def __init__(self, left=None, right=None):
        self.left:Expression = left
        self.right:Expression = right


def findOper(elems:list[Elem], oper:str):
    ''' find first oper between words and brackets'''

    inBr = 0
    obr = '([{'
    cbr = '}])'
    
    for i in range(len(elems)):
        ee = elems[i]
        # if ee.type != Lt.oper:
        #     continue
        if ee.type == Lt.oper and ee.text in obr:
            inBr += 1
            continue
        if ee.type == Lt.oper and ee.text in cbr:
            inBr -= 1
            continue
        if inBr:
            continue
        if ee.text == oper:
            return i
        if i > 0:
            return i
    return -1


class CaseArrowR(SubCase):
    ''' multi pattern 
        1. lambda case
            \arg -> expr
        2. case of match:
            expr -> expr
        3. put elem to collection (?)
            12 -> array
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''
        expr -> expr '''
        if len(elems) < 2:
            return False
        oper = '->'
        oind = findOper(elems, oper)
        print('# match-found: ', oind)
        if oind < 1:
            return False
        
        return elems[oind].text == oper

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        arrInd = findOper(elems, '->')
        exp = ArrOper()
        subs = [elems[:arrInd], elems[arrInd+1:]]
        return exp, subs

    def setSub(self, base:ArrOper, subs:list[Expression])->Expression:
        base.left = subs[0]
        if len(subs) > 1 and isinstance(subs[1], Expression):
            base.right = subs[1]


class CaseFor(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'for':
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subs = []
        start = 1
        elen = len(elems)
        _, subs = CaseSemic().split(elems[1:])

        exp:LoopBlock = None
        match len(subs):
            case 1: exp = LoopIterExpr()
            case 2|3: exp = LoopExpr()
            case _ :pass
        print('# CaseFor.split-', elen,  exp, 'len-subs=', len(subs))
        for ees in subs:
            prels('>>', ees)
        return exp, subs
    
    def setSub(self, base:LoopExpr, subs:Expression|list[Expression])->Expression:
        ''' nothing in minimal impl''' 
        slen = len(subs)
        print('# CaseFor.setSub-', slen, subs)
        match slen:
            # iterator case
            case 1 if isinstance(base, LoopIterExpr):
                base.setIter(subs[0])
                print('(=1)', subs[0], subs[0].srcExpr )
            # pre, cond
            case 2 if isinstance(base, LoopExpr): base.setExpr(pre=subs[0], cond=subs[1])
            # init, cond, post
            case 3 if isinstance(base, LoopExpr): base.setExpr(init=subs[0], cond=subs[1], post=subs[2])
        print('# CaseFor.setSub-', base)
        return base

class CaseIf(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'if':
            return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = IfExpr()
        return exp, [elems[1:]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        base.setCond(subs[0])
        return base


class CaseWhile(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'while':
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = WhileExpr()
        return exp, [elems[1:]]

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        base.setCond(subs[0])
        return base


class CaseElse(BlockCase, SubCase):
    ''' 
    in base impl no else with sub condition:
    if cond
        code
    else
        if cond
            code
        else
            code
    
    '''
        
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'else':
            # TODO: possible case in feature: else if sub-cond
            return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ElseExpr()
        return exp,[elems[1:]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' nothing in minimal impl''' 
        # base.setCond(subs[0])
        return base


