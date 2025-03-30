
'''

'''

from nodes.iternodes import IterGen


def loop_iter(*args):
    beg, over, step = 0, 0, 1
    match len(args):
        case 1: over = args[0]
        case 2: beg, over = args
        case 3: beg, over, step = args
    it = IterGen(beg, over, step)
    return it

