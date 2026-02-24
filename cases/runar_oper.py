'''
Right-associated unary operators

expression <operator>
'''


from lang import *
from vars import *
from vals import elem2val, isLex

from cases.utils import *
from cases.tcases import *
from nodes.func_opers import *
from nodes.tnodes import *


class CaseRTildArroy(SubCase, SolidCase):
    ''' solid~> '''
    # RTildArrowExpr
    
    def match(self, elems:list[Elem]) -> bool:
        ''' '''
        if len(elems) < 2:
            return False
        return isLex(elems[-1], Lt.oper, '~>')
        

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # fname = elems[-1].text
        # member = VarExpr(Var(fname, TypeAny()))
        expr = RTildArrowExpr()
        return expr, [elems[:-1]]
    
    def setSub(self, base:RTildArrowExpr, subs:Expression|list[Expression])->Expression: 
        ''' '''
        sub = subs[0]
        # print('O.dot:setSub', objExpr)
        base.setInner(sub)
        return base


class CaseArgExtraList(SubCase, SolidCase):
    ''' varname... '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 2:
            return False
        if not isSolidExpr(elems[:-1]):
            return False
        # print('CaseArgExtraList', isSolidExpr(elems[:-1]), elemStr(elems[:-1]))
        # print('$2 ', )
        if isLex(elems[-1], Lt.oper, '...'):
            return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
    # def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        avar = None
        subs = []
        if len(elems) == 2:
            avar = VarExpr(ArgSetOrd(elems[0].text))
        else:
            subs = [elems[:-1]]
        # dirty huck here. avar can be arg in def,  and val in call
        expr = ArgExtList(avar)
        return expr, subs

    def setSub(self, base:ArgExtList, subs:Expression|list[Expression])->Expression:
        if subs:
            base.setSub(subs[0])


class CaseArgExtraDict(ExpCase):
    '''
    Not used.
    ${varname} varname{...}  varname^ varname..> varname..~ dd^^ dd?.. <dd> dd$$ dd~~
    ''' 
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) != 2:
            return False
        if elems[0].type == Lt.word and isLex(elems[1], Lt.oper, '$$'):
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        # expr = VarExpr(Var(elems[0].text, TypeAny()))
        # return expr


class RUnaryOper(SubCase, SolidCase):
    ''' n...  '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 2:
            return False
        if not isSolidExpr(elems[:-1]):
            return False
        if isLex(elems[-1], Lt.oper, '...'):
            return True
        return False
    
    def getExpr(self, oper):
        match oper:
            case '...':
                return ArgExtList()
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
    # def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        subs = []
        subs = [elems[:-1]]
        oper = elems[-1].text
        
        expr = self.getExpr(oper)
        return expr, subs

    def setSub(self, base:ArgExtList, subs:Expression|list[Expression])->Expression:
        if subs:
            base.setSub(subs[0])

