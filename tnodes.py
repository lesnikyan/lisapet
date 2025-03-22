
"""
Structural components of execution tree.
"""

from lang import *
from vars import *
from expression import *

class Node:
    def __init__(self):
        command = 0
        arg = 0
        


# Expression

class CollectionExpr(Expression):
    ''''''
    def addVal(self, val:Var):
        pass
    
    def setVal(self, index:Var, val:Var):
        pass

    def getVal(self, index:Var):
        pass


class ListExpr(CollectionExpr):
    ''' [1,2,3, var, foo(), []]
    Make `list` object 
    '''
    def __init__(self):
        self.valsExprList:list[Expression] = []
        self.listObj:ListVar = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        self.valsExprList.append(exp)

    def do(self, ctx:Context):
        self.listObj = ListVar(None)
        print('## ListExpr.do1 self.listObj:', self.listObj, 'size:', len(self.valsExprList))
        for exp in self.valsExprList:
            exp.do(ctx)
            self.listObj.addVal(exp.get())
        print('## ListExpr.do2 self.listObj:', self.listObj)

    def get(self):
        print('## ListExpr.get self.listObj:', self.listObj)
        return self.listObj



class DictExpr(CollectionExpr):
    ''' {'key': val, keyVar: 13, foo():bar()} '''


class TupleExpr(CollectionExpr):
    ''' res = (a, b, c); res = a, b, c '''


class Matching(Expression):
    ''' 
    1. for unpack multiresults.
    2. for pattern matching like switch/case '''


class Module(Block):
    ''' Level of one file. 
    functions, constants, structs with methods '''
    def __init__(self):
        super().__init__()
        self.imported:dict[str, Context] = {}

    # def do(self):
    #     self.lastVal = None
    #     # TODO: eval sequences one by one, store result of each line, change vars in contexts

    # def get(self) -> list[Var]:
    #     return None

    def importIn(self, name, module):
        ''' Add other modules here'''
        self.imported[name] = module
        # TODO: merge contexts by resolved names
        
    def exportOut(self):
        ''' Call from other module `importIn '''
        return self.ctx

