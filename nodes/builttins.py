
'''

'''

from nodes.iternodes import *


def loop_iter(*args):
    beg, over, step = 0, 0, 1
    print('>>>>>>>>>>>>>>>>> loop_iter function')
    match len(args):
        case 1: over = args[0]
        case 2: beg, over = args
        case 3: beg, over, step = args
    it = IndexIterator(beg, over, step)
    return it

# def buit_print(*args):
#     pargs = []
#     for n in args:
#         if isinstance()
#         data = []
        