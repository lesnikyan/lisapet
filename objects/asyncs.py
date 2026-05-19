'''' '''

import asyncio
import concurrent.futures as cft

from lang import *
from base import *
from typex import *
from vars import ValQueue
from context import Context


class ChanVal(ValQueue):
    def __init__(self):
        super().__init__(None, TypeChan)
        self._q:asyncio.Queue = asyncio.Queue()
        self.loop:asyncio.AbstractEventLoop = None
    
    def setLoop(self, loop):
        self.loop = loop
    
    async def aput(self, val:Val):
        await self._q.put(val)
    
    def put(self, val:Val):
        ''' put elem to the end '''
        # print(113)
        v:cft.Future = asyncio.run_coroutine_threadsafe(self.aput(val), self.loop)
        cft.wait([v])

    async def aget(self):
        return await self._q.get()

    def get(self):
        ''' return first elem '''
        # print(103)
        v:cft.Future = asyncio.run_coroutine_threadsafe(self.aget(), self.loop)
        dv = cft.wait([v])
        r = dv.done.pop().result()
        # print(104, r)
        return r
    
    def isEmpty(self):
        ''' '''
        return Val(self._q.empty(),  TypeBool())
    
    def len(self):
        ''' count of elems '''
        return Val(self._q.qsize(), TypeInt())


class Coroutine:
    
    def __init__(self, func = None):
        self.func:FuncInst = func
    
    def do(self):
        self.func.do(None)
    

class Runner:
    def __init__(self):
        self.items:list[Coroutine] = []
        self.loop = None
        self.chans:list[ChanVal] = []
    
    def add(self, coro:Coroutine):
        self.items.append(coro)
    
    def addChan(self, chan):
        self.chans.append(chan)
    
    async def irunner(self):
        self.loop = asyncio.get_running_loop()
        self.runInit()
        tt = []
        for coro in self.items:
            t = self.loop.run_in_executor(None, coro.do)
            tt.append(t)
            # print(101)
        for t in tt:
            await t
    
    def runInit(self):
        for n in self.chans:
            n.setLoop(self.loop)
    
    def run(self, ctx:Context=None):
        asyncio.run(self.irunner())

