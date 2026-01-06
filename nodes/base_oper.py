'''

'''

from lang import *
from vars import *
from nodes.expression import *
from bases.ntype import *


class OperCommand(Expression):
    
    def __init__(self, oper):
        super().__init__(oper)
        self.src = ''
        self.oper:str = oper
        self.res = None
        self.__block = False

    def get(self):
        # print('# -> OperCommand.get() ', self.oper, self.res)
        return self.res


class BinOper(OperCommand):

    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper)
        # self.oper = oper
        self.left:Expression = left
        self.right:Expression = right

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        # dprint('BinOper.setArgs', left, right)
        self.left = left
        self.right = right
    
    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.right.add(expr)


class AssignExpr(BinOper):
    ''' a = x'''

