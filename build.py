'''
Build code from source.
CI - build code from file or line.
'''

from argparse import ArgumentParser
from pathlib import Path

from lang import CLine, dprint
from parser import splitLexems, elemStream
from tree import lex2tree
from nodes.expression import Expression
# from nodes.tnodes import Module


def filepath(fname):
    return Path(__file__).cwd() / fname


def getArgs():
    arp = ArgumentParser()
    arp.add_argument('filename')
    arp.add_argument('-c', '--codeline', action="store_true",
                     help='Execute line of code.') # in line code
    args = arp.parse_args()
    return args


def readFile(filename):
    '''return file content'''
    fpath = filepath(filename)
    with open(fpath, 'r') as fr:
        return fr.read()


def buildTree(src):
    '''Parse and build executable tree.'''
    tlines = splitLexems(src)
    clines:CLine = elemStream(tlines)
    exp = lex2tree(clines)
    return exp

def buildFile(filename):
    '''Read file and build exec tree'''
    src = readFile(filename)
    return buildTree(src)


def tree2bin(expr:Expression):
    '''Serialize exec tree.'''
    # TODO: think about protobufs


def storeExpression(expr:Expression, filename):
    '''Store exec tree into file.'''


def main():
    ''' Run script using args from command line '''
    try:
        args = getArgs()
        # TODO: build to binary. We need appropriate serialization format. 
    except Exception as ex:
        dprint("Error happened in building process.", ex)


if __name__ == '__main__':
    main()
