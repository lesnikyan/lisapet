
from lang import *
from nodes.builtins import *
from context import Context


def dict_keys(_, dval:DictVal) -> ListVal:
    return dval.keys()
    
def dict_items(_, dval:DictVal):
      return dval.items()

