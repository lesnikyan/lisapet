''' '''

from vars import *
from nodes.expression import *
from nodes.func_expr import *

# Definitions

class Definition:
    def __init__(self, name:str):
        self.name = name

    def inst(self, ctx:Context):
        pass

class TypeDef(Definition):
    def __init__(self):
        pass

    def inst(self, ctx:Context):
        pass

class Struct:
    def __init__(self, names:list[str]):
        self.names = names
        self.fields:dict[str, Var] = {}
        
    def set(self, name, val:Var):
        if name in self.names:
            self.fields[name] = val

    def get(self, name)->Var:
        return self.fields[name]

class StructDef(TypeDef):
    def __init__(self):
        pass

    def inst(self, ctx:Context, args:list[Var]):
        return Struct(args)


# class FuncDef(Definition):
#     def __init__(self, name, fargs:list[Var]=None):
#         super().__init__(name)
#         self.args = fargs
#         self.block = Block()

#     def inst(self, paretnCtx:Context)->Func:
#         return Func(self.block, self.args, paretnCtx)
