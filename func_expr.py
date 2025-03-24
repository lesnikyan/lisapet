
from vars import *
from expression import *

# Function

# class Func(Base):
#     ''' Callable object '''
    
#     def __init__(self, block:Block=None, fargs:list[Var]=None, pCtx:Context=None):
#         self.block = block if block else Block() # inner Block
#         if not pCtx:
#             pCtx = Context()
#         self.parentCtx = pCtx # context of upper level: high-order func, struct, module, other namespace
#         self.ctx:Context = Context() # Args
#         self.setArgs(fargs)
#         self.lastRes = None

#     def setArgs(self, fargs:list[Var]):
#         self.ctx.add(fargs)

#     def add(self, seq:Expression|list[Expression]):
#         self.block.add(seq)

#     def do(self, ctx:Context, args: Context):
#         ''' eval block
#         ctx - upper global context
#         args - context with arguments
#         '''
#         # merge/nest contexts
#         funCtx = Context(ctx)
#         funCtx.update({k:v for k, v in args.vars}) 
#         self.block.do(funCtx)
#         self.lastRes = self.block.res()

#     def get(self):
#         return self.lastRes


# class FuncExpr(Expression):
#     ''' Call func expression '''
#     def __init__(self, func:Func, args:list[Expression]):
#         # super().__init__()
#         self.func:Func = func
#         self.agrExpr = args
    
#     def do(self, ctx:Context):
#         args = [Expression()] 
#         # TODO: implement getting vals from context and self.argExpr
#         # set agrs to inner context
#         self.func.do(ctx, args)

