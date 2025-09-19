'''
Options:
1. Build and eval script.
run.py filename.et 
-b binfile.etb: build only into binfile
run.py filename.etb (execute previously built file)
'''

# TODO: think about interactive mode

# TODO: add pass of CI args for ET code.

# TODO: add iterative call of built code.


import argparse
from argparse import ArgumentParser
import lang
import json
from pathlib import Path

from lang import *
import loader
from base import Val, Var, InterpretErr, EvalErr, XDebug
from typex import valType
from vars import ListVal, DictVal, TupleVal
from context import Context, RootContext
from nodes.expression import Expression, expSrc
from nodes.tnodes import Module
from build import buildTree, readFile
from eval import rootContext


def getArgs():
    arp = ArgumentParser()
    arp.add_argument('src')
    arp.add_argument('-c', '--codeline', action="store_true",
                     help='Execute line of code.') # in line code
    arp.add_argument('-i', '--imports',
                     help='Import list over space.')
    arp.add_argument('-p', '--pathroot',
                     help='Import list over space.')
    arp.add_argument('-e', '--show-error', action="store_true",
                     help='Show native error traceback.')
    arp.add_argument('-l', '--multirun', action="store_true",
                     help='Execute multiple times by source. Needs one of data sources: code, file, json')
    arp.add_argument('-s', '--datasource',
                     help='String with code that produces data list.')
    arp.add_argument('-f', '--json-file',
                     help='Path to json file.')
    arp.add_argument('-j', '--json-source',
                     help='Json data in string.')
    arp.add_argument('-r', '--result',
                     help='Result: show result by passed var name.')
    args = arp.parse_args()
    return args


def getSource(args):
    '''Read line or file.'''
    if args.codeline:
        return args.src
    fname = args.src
    src:Module = readFile(fname)
    return src


# def getContext():
#     '''Prepare context.'''
#     croot = rootContext()
#     cur = croot.moduleContext()
#     return cur


def readDataSource(args):
    '''
    -s --datasource "source" # string with et-code, result var by default is `result`
        [1..100] # if list of simple vals (int, str) - each val will be converted into var `x`, otherwize - each val should be a dict
    -x --exec-source # executable et-file with function `func source` that producec list of scalar vals, or list of dicts
    -f -json-file ''  # path to json file
    -j -json-source '{}' # string with json
    '''
    data = []
    if args.json_source:
        src = args.json_source
        # print('src:', src, type(src))
        data = json.loads(src)
        # print('data:', data, type(data))
        return data
    if args.datasource:
        code = args.datasource
        # if code is a generator: [1..100]
        code = f"tolist({code})"
        # store result
        code = f"result = {code}"
        # print('code:', code)
        # eval code, read data
        expr = buildTree(code)
        ctx = rootContext().moduleContext()
        expr.do(ctx)
        res = readResult(ctx, 'result')
        # print('data-res:', res)
        return res
    if args.json_file:
        src = readFile(args.json_file)
        data = json.loads(src)
        return data
    return data


def setVars(data:dict, ctx:Context):
    vars = {}
    for name, v in data.items():
        vtype = valType(v)
        vv = Val(v, vtype)
        vars[name] = vv
    ctx.addSet(vars)


def readResult(ctx:Context, rname):
    ''' '''
    if not rname:
        return None
    resVal = None
    rvar = ctx.get(rname).get()
    if isinstance(rvar,(ListVal, DictVal, TupleVal)):
        resVal = rvar.vals()
    elif (isinstance(rvar, (Val, Var))):
        resVal = rvar.getVal()
    return resVal


def multirun(expr:Expression, data:list, ctx:Context):
    '''
        -l --multirun 
        data - [{key:val},...]
    '''
    print('data:', data)
    for vars in data:
        # if just one value in item
        if not isinstance(vars, dict):
            vars = {'x': vars}
        setVars(vars, ctx)
        expr.do(ctx)


def run(expr:Expression, ctx:Context):
    '''
    Execute built expression
    '''
    expr.do(ctx)


def importHeads(line:str):
    
    # split imports
    lines = line.split(';')
    srcLines = ['import %s' % s.strip() for s in lines]
    src = "\n".join(srcLines)
    # print('::\n', src)
    return src


def importPreload(args, rctx:RootContext):
    '''
    Preload modules.
    Import loaded modules to context.
    -i "dir.mod1; dir.dir.mod2; dir.mod3 > fun1, type2 t2;"
    '''
    # get from args
    modArg = args.imports
    src = importHeads(modArg)
    return src
    # load modules
    # buildTree(src, rctx)


def main():
    ''' Run script using args from command line
        -r -result # read result var, name of result var (var should be defined in code)
    '''
    args = getArgs()
    src = getSource(args)
    expr = None
    try:
        # test file root
        basePath = Path(__file__).parent
        if args.pathroot:
            basePath = args.pathroot
        loader.modRoot = basePath
        rCtx = rootContext()
        head = ''
        if args.imports:
            importPreload(args, rCtx)
            modArg = args.imports
            head = importHeads(modArg) + '\n'
        # lang.FullPrint = 1
        src = '%s%s' % (head, src)
        expr = buildTree(src, rCtx)
        # TODO: here: add importable modules into root ctx
        ctx = rCtx.moduleContext()
        if args.multirun:
            srcData = readDataSource(args)
            multirun(expr, srcData, ctx)
        else:
            run(expr, ctx)
        # print('args.result:', args.result)
        print('run: Ok')
        if args.result:
            res = readResult(ctx, args.result)
            print('>>', res)
    except ParseErr as exc:
        print('Error in parsing: ', exc.msg)
        print("in line:\n", exc.src.src)
        if args.show_error:
            raise exc
        
    except InterpretErr as exc:
        print('Error interpretation: ', exc.msg)
        exSrc = expSrc(exc.src)
        print("in line:\n", exSrc)
        if exc.parent:
            print('Caused by error:', exc)
            if args.show_error:
                raise exc.parent
        if args.show_error:
            raise exc
                
    except EvalErr as exc:
        print("Execute error:", exc.msg)
        if expr and isinstance(expr, Expression):
            lineExpr = expr
            print("in line:\n", lineExpr.src.src)
        if args.show_error:
            raise exc
            
    except Exception as exc:
        print('Error handling: ', exc)
        if args.show_error:
            raise exc


if __name__ == '__main__':
    main()
