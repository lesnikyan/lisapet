
"""
Structural components of execution tree.
"""

from lang import *
from vars import *
from nodes.expression import *


# Expression




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
        
    # def exportOut(self):
    #     ''' Call from other module `importIn '''
    #     return self.ctx

