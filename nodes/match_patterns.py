
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

    def setExp(self, exp:Exception):
        pass
    
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
        # print('MCVal.exp', self.exp, ' >>', val)
        if self.exp.get().getVal() == val.getVal():
            return True
        return False
    
class MC_Other(MatchingPattern):
    ''' _ !- ... '''

    def do(self, ctx:Context):
        # print('case-other.do')
        pass
        
    def match(self, val:Val):
        return True


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