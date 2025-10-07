
'''
Expressions of PatterMatch cases

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.iternodes import *
from nodes.keywords import *



# MATCH-CASE



class MCaseExpression(Expression):
    ''' '''


class MatchingPattern(Expression):
    ''' '''
    
    def __init__(self, src=None):
        super().__init__(None, src)

    # def setExp(self, exp:Exception):
    #     pass
    
    def match(self, val:Val):
        pass
    
    # def do(self, ctx:Context):
    #     pass
    
class MCValue(MatchingPattern):
    ''' 123 !- ... '''
    def __init__(self, expVal:Expression,  src=None):
        super().__init__(src)
        self.exp:Expression = expVal

    # def setExp(self, exp:Exception):
    #     self.exp = exp

    def do(self, ctx:Context):
        # print('MCVal.exp', self.exp)
        self.exp.do(ctx)
        
    def match(self, val:Val):
        # print('MCVal.exp', self.exp, self.exp.get(), ' >>', val)
        # if not scalar or string
        vtype = val.getType()
        if not isinstance(vtype, (TypeNum, TypeInt, TypeNull, TypeBool, TypeString)):
            # print('MCVal.match bad type', vtype, isinstance(vtype, TypeInt))
            return False
        if self.exp.get().getVal() == val.get():
            return True
        return False
    
class MC_Other(MatchingPattern):
    ''' _ !- ... '''

    def do(self, ctx:Context):
        # print('case-other.do')
        pass
        
    def match(self, val:Val):
        return True

class MCElem(MatchingPattern):
    ''' element of complex pattern '''

class MCSubVar(MCElem):
    ''' local subvar in pattern like: [a,b,c] '''

    def __init__(self, expVar:VarExpr,  src=None):
        super().__init__(src)
        self.exp:VarExpr = expVar
        self.var:Var = None

    def do(self, ctx:Context):
        # print('elem subvar.do')
        self.exp.do(ctx)
        self.var = self.exp.get()
        
    def match(self, val:Val):
        self.var.set(val)
        self.var.setType(val.getType())
        return True

class MC_under(MCElem):
    ''' _ '''

    def do(self, ctx:Context):
        # print('elem `_`.do')
        pass
        
    def match(self, val:Val):
        return True

class MCContr(MatchingPattern):
    ''' pattern with sub-elements:
    collections, struct, etc'''
    
    def addSub(self, sub:MCElem):
        pass


class MCSerialVals(MCContr):
    ''' Pattern of serial set of values.
        basically: list, tuple
    '''
    
    def __init__(self,  src=None):
        super().__init__(src)
        self.elems:list[MCElem] = []

    def matchSerial(self, val:ListVal|TupleVal):
        vals = val.rawVals()
        vi = -1
        lenv = len(vals)
        for elem in self.elems:
            vi += 1
            if vi >= lenv:
                # pattern longer than value
                return False
            velem = vals[vi]
            if not elem.match(velem):
                return False
        if vi < (lenv - 1):
            # value longer than pattern
            return False
        return True


class MCList(MCSerialVals):
    ''' [], [123], [a,b], [_], [?], [*] '''
    
    def __init__(self,  src=None):
        super().__init__(src)

    def do(self, ctx:Context):
        # print('MCVal.exp', self.exp)
        for exp in self.elems:
            exp.do(ctx)
        
    def match(self, val:ListVal):
        if not isinstance(val.getType(), TypeList):
            return False
        return self.matchSerial(val)
    
    def addSub(self, sub:MCElem):
        self.elems.append(sub)


class MCTuple(MCSerialVals):
    ''' [], [123], [a,b], [_], [?], [*] '''
    
    def __init__(self,  src=None):
        super().__init__(src)

    def do(self, ctx:Context):
        for exp in self.elems:
            exp.do(ctx)
        
    def match(self, val:ListVal):
        if not isinstance(val.getType(), TypeTuple):
            return False
        
        return self.matchSerial(val)
    
    def addSub(self, sub:MCElem):
        self.elems.append(sub)

# -----------------

    
class MCStar(MCElem):
    ''' * '''

    def do(self, ctx:Context):
        # print('elem `*`.do')
        pass
        
    def match(self, val:Val|list[Val]):
        return True
    
class MCQMark(MCElem):
    ''' ? '''

    def do(self, ctx:Context):
        # print('elem `?`.do')
        pass
        
    def match(self, val:Val):
        return True

# --------------------

class CaseExpr(ControlBlock):
    ''' case in `match` block
    '''
    
    # TODO: do we need result from `match` blok?

    def __init__(self):
        # super().__init__()
        self.block = Block()
        self.expect:MatchingPattern = None
        # self.pattern:MatchingPattern = None

    def setExp(self, exp:Exception):
        # print('CaseExpr.setExp:', exp)
        self.expect = exp

    def doExp(self, ctx:Context):
        self.expect.do(ctx)

    def match(self, val:Val):
        # simple equal value
        # print('~~~ %s == %s >>  %s' % (self.expect.get(), val.get(), self.expect.get() == val.get()))
        # print('~~~ ', self.expect)
        # if self.expect.get().getVal() == val.getVal():
        #     return True
        
        return self.expect.match(val)

        # # type case
        # et = self.expect.get()
        # if isinstance(et, VType) and et == val.getType():
        #     return True

        # TODO: 
        
        # list case
        
        # tuple case
        
        # dict case
        
        # struct-constructor case
        
        # return False

    def add(self, exp:Expression):
        self.block.add(exp)
    
    def do(self, ctx:Context):
        ''' body of sub-block '''
        self.block.do(ctx)
        self.lastVal = self.block.get()