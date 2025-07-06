'''
Options:
1. Build and eval script.
run.py filename.et 
-b binfile.etb: build only into binfile
run.py filename.etb (execute previously built file)
'''

# TODO: think about interactive mode

import argparse
from argparse import ArgumentParser

from context import Context
from nodes.expression import Expression
from nodes.tnodes import Module
from build import buildTree, readFile
from eval import rootContext


def getArgs():
    arp = ArgumentParser()
    arp.add_argument('src')
    arp.add_argument('-c', '--codeline', action="store_true",
                     help='Execute line of code.') # in line code
    args = arp.parse_args()
    return args


def getSource(args):
    '''Read line or file.'''
    if args.codeline:
        return args.src
    fname = args.src
    src:Module = readFile(fname)
    return src


def getContext():
    '''Prepare context.'''
    croot = rootContext()
    cur = croot.moduleContext()
    return cur


def exec(tree:Expression, ctx:Context):
    '''Execute built expression'''
    tree.do(ctx)


def main():
    ''' Run script using args from command line '''
    args = getArgs()
    src = getSource(args)
    expr = buildTree(src)
    rCtx = rootContext()
    # TODO: here: add importable modules into root ctx
    ctx = rCtx.moduleContext()
    exec(expr, ctx)


if __name__ == '__main__':
    main()
