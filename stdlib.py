
'''
Basic useful functions
'''

from collections.abc import Collable

from eval import Func, Block, Var, VType, Undefined, null



class StdBlock(Block):
    def __init__(self, func:Collable, farg:list[Var], resType:VType):
        self.func = func
        super().__init__()
        self.args = farg
    
    def do(self):
        res = self.func(*self.args)
        if not isinstance(res, (list, tuple)):
            res = [res]
            res = [Var(n) for n in res]
        self.lastVal = res

def stdFunc(func:Collable, args:list[Var]=None)->Func:
    ''' '''
    return Func(StdBlock(func, args, null))

FUNCTIONS:dict[str,Func] = {
    'print' : stdFunc(print), # console output,
    'fstr' : None, # format string
    'read' : None, # read bytes from reader
    'write': None, # write bytes to writer
    'open' : None, # open byte stream, return reader
    'close': None, # close reader|writer
    'compare': None, 
    'nothing': None # empty call, do nothing
}
