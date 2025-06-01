
'''
Basic useful functions
'''

from collections.abc import  Callable

# from eval import Func, Block, Var, VType, Undefined, null
from nodes.expression import Block, Expression
from nodes.func_expr import Function
from vars import *



class StdBlock(Block):
    def __init__(self, func:Callable, farg:list[Var], resType:VType):
        self.func = func
        super().__init__()
        self.args = farg
    
    def do(self):
        res = self.func(*self.args)
        if not isinstance(res, (list, tuple)):
            res = [res]
        res = [Var(n, TypeAny()) for n in res]
        self.lastVal = res

def stdFunc(func:Callable, args:list[Var]=None)->Function:
    ''' '''
    return Function(StdBlock(func, args, None))

FUNCTIONS:dict[str,Function] = {
    'print' : stdFunc(print), # console output,
    'fstr' : None, # format string
    'read' : None, # read bytes from reader
    'write': None, # write bytes to writer
    'open' : None, # open byte stream, return reader
    'close': None, # close reader|writer
    'compare': None, 
    'nothing': None # empty call, do nothing
}
