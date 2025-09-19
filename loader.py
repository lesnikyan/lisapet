
'''
Interpretation loader.
'''


from argparse import ArgumentParser
import os
from pathlib import Path

from lang import CLine, dprint
from parser import splitLexems, elemStream
from tree import lex2tree
from context import Context, ModuleContext, RootContext
from cases.tcases import CaseImport
from vals import isLex
from nodes.expression import Expression
from nodes.tnodes import Module
from eval import rootContext


cimp = CaseImport()
rootCtx = rootContext()

modRoot = ''

def filePath(root, modFile):
    return os.path.join(root, modFile)


def getLibRoot():
    # common store: used-defined dir with all installed liraries.
    # can be defined by 
    # config (TODO: add config) or 
    # env var (TODO) or
    # CI arg (TODO).
    return ''


def readFile(fpath):
    '''return file content'''
    # fpath = filepath(filename)
    with open(fpath, 'r') as fr:
        return fr.read()


def buildFile(rctx: RootContext, path):
    '''Read file and build exec tree'''
    # print('buildFile:', path)
    src = readFile(path)
    return buildTree(src, rctx)


def modPreload(rctx: RootContext, modPath:str, root=None, name = ''):
    rootPath = modRoot # TODO: 1) local dir, 2) common store 
    if root:
        rootPath = root
    # print('modPreload:', rootPath, modPath)
    fpath = os.path.join(rootPath, modPath)
    mod = buildFile(rctx, fpath)
    mod.name = name
    rctx.loadModule(mod)
    return mod


def loadModules(lines:list[CLine], rctx:RootContext):
    ''' TODO: we have to detect `import` command and preload importing modules here.
    Looks like we need to use for preloading the same mechanism because
    declaretions of structs need to be loaded into context 
    before correct interpretation of structs contructors.
    '''
    for s in lines:
        if cimp.match(s.code):
            # parse import line
            impPath, _ = cimp.splitElems(s.code[1:])
            modName = impPath[-1]
            # print('impPath:', impPath)
            fpath = cimp.fileByPath(impPath)
            # load module
            modPreload(rctx, fpath, name=modName)


def buildTree(src, rctx: RootContext=None):
    '''Parse and build executable tree.
    rctx: RootContext - not needed if no imports in source code
    '''
    tlines = splitLexems(src)
    clines:list[CLine] = elemStream(tlines)
    # rootCtx = rootContext()
    loadModules(clines, rctx)
    exp = lex2tree(clines)
    return exp


