'''
inline (prefix) modifiers

mod expr
'''



from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from nodes.tnodes import *
# from nodes.keywords import ConstVarExpr

from cases.tcases import *
# from cases.oper import *
# from cases.structs import MethodDefExpr
# from cases.utils import OperSplitter



class CaseConst(ExpCase):
    ''' const var
        const is a prefix-modefier with '''
    def __init__(self):
        super().__init__()
        self.cv = CaseVar()
        # self.lastPos = None
        self.pref = 'const'
        self.esize = [2,4]

    def match(self, elems:list[Elem], ind=None) -> bool:
        ''' const var '''
        if len(elems) not in self.esize:
            return
        if not isLex(elems[0], Lt.word, self.pref):
            return False
        
        return self.cv.match(elems[1:])

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        varExpr = self.cv.expr(elems[1:])
        varExpr.const = True
        return varExpr
        # expr = ConstVarExpr(varExpr, src=elems)
        # return expr
    
    # def setSub(self, base:ConstVarExpr, subs:Expression|list[Expression])->Expression: 
    #     ''' base - FuncCallExpr, subs - argVal expressions '''
    #     return base
        
        