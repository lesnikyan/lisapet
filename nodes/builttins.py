
'''

'''

from nodes.iternodes import *


def loop_iter(*args):
    beg, over, step = Val(0, None), Val(0, None), Val(1, None)
    print('>>>>>>>>>>>>>>>>> loop_iter function')
    match len(args):
        case 1: over = args[0]
        case 2: beg, over = args
        case 3: beg, over, step = args
    it = IndexIterator(beg.get(), over.get(), step.get())
    return it

# def buit_print(*args):
#     pargs = []
#     for n in args:
#         if isinstance()
#         data = []
        

def buit_len(arg):
    return arg.len()


def built_int(x):
    return int(x.getVal())


