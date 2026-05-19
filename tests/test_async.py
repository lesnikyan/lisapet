
from unittest import TestCase, main

# import asyncio
# import concurrent.futures as cft

import time

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from context import Context
from bases.strformat import *
# from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from bases.over_ctx import FuncOverSet
from tests.utils import *
from libs.regexp import *
from nodes.func_features import *

from objects.asyncs import *

import cProfile as prof
import pdb



def tsleep(n):
    time.sleep(n)


class TT:
    def __init__(self):
        self.data = []
        
    def print(self, *args):
        self.data.append(args)



class TestAsync(TestCase):
    
    '''
    TODO: chan as iterable
    
    TODO: close chan, stop loop by chan
    
    TODO: chan: .isEmpty(), .size(), .isFull(), .isClosed()
    
    TODO: channels selector, should take 1-st added val from several channels
    
    TODO: callback by finished coroutine
    
    '''

    def test_runner_with_coroutines(self):
        ''' test manually made coroutines, Runner 
            and channel between functions '''
            

        tp1 = TT()

        # writting to chan
        def foo(ctx:Context, wchan:ChanVal):
            for i in range(4):
                n = i + 10
                tp1.print('foo, ch <-', i, ':', n)
                tsleep(0.001)
                wchan.put(Val(n, TypeInt()))
                tsleep(0.003)

        # reading from chan
        def bar(ctx, rchan:ChanVal):
            for i in range(4):
                v = rchan.get()
                tp1.print('bar, <- ch', i, v.get())
                tsleep(0.002)
            
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ch = ChanVal()
        fn = setNativeFunc(ctx, 'foo', foo, TypeNull())
        fn.setArgVals([ch])
        cr1 = Coroutine(fn)
        f2 = setNativeFunc(ctx, 'bar', bar, TypeNull())
        f2.setArgVals([ch])
        cr2 = Coroutine(f2)
        rnr = Runner()
        rnr.addChan(ch)
        rnr.add(cr1)
        rnr.add(cr2)
        # print('tt> 01')
        rnr.run()
        # print('tt> 02')
        # time.sleep(0.1)
        # print(tp1.data)
        exp = [
            ('foo, ch <-', 0, ':', 10), ('bar, <- ch', 0, 10), 
            ('foo, ch <-', 1, ':', 11), ('bar, <- ch', 1, 11), 
            ('foo, ch <-', 2, ':', 12), ('bar, <- ch', 2, 12), 
            ('foo, ch <-', 3, ':', 13), ('bar, <- ch', 3, 13)]
        self.assertEqual(exp, tp1.data)


    def _test_2(self):
        ''' '''
        code = r'''
        res = []
        s = (: n; n <- [1..5])
        res <-- s # next/get from right, put/append to left
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        print(resv)
        exv = []
        # self.assertEqual(exv, resv)

if __name__ == '__main__':
    main()

