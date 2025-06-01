

from lang import *
from vars import *
from nodes.expression import *
from context import Context, ModuleContext
from nodes.tnodes import Module

class EvalEnv:
    '''
    Importing:
    1. Load code from file.
    2. Convert code to Module tree.
    3. Add Module to dict env.modules.
    4. During eval `import` expr: find module in env.dict 
    5. call module.do(mctx) with its own mctx:Context.
    6. Add mctx to context of module where `import` expression has been called.
    7. Add mctx of imported module to the `imported` dict in current context.
    8. imported names:
        a) if basic `import module_name: use dot-operator to access names in imported module
        b) if `import module_name.*`: all names from imported module should be available by internal names
        c) if `import module_name > name1, name2, name3 alias3`: 
            only listed names should be available, aliases will be stored into additional dict {alias:origin, }
    '''
    
    def __init__(self):
        self.modules:dict[str, Module] = {}
        
    def addModule(self, mod:Module):
        self.modules[mod.name] = mod
    
    
