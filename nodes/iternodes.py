
'''
Iteration expressions.
Mostly for usage into for-loop or generators.
'''

from lang import *
from vars import *
from vals import *

from nodes.base_oper import BinOper
from nodes.expression import *
from nodes.oper_nodes import OpAssign
# from nodes.func_expr import FuncCallExpr
# import nodes.datanodes
from nodes.datanodes import DictVal, ListVal, TupleVal


class NIterator:
    ''' '''
    
    def start(self):
        ''' reset iterator to start position '''
        pass

    def step(self):
        ''' move to next pos '''
        pass

    def hasNext(self):
        ''' if not last position '''
        pass

    def get(self):
        ''' get current element '''
        pass


class IterAssignExpr(Expression):
    ''' target <- iter|collection '''
    def __init__(self):
        # self.assignExpr:Expression = None
        self.itExp:NIterator = None # right part, iterator
        self.srcExpr:CollectionExpr = None # right part, collection constructor, func(), var
        # local vars in: key, val <- iterExpr
        self.key:Var = None
        self.val:Var = None
        self._first_iter = False

    def setArgs(self, target, src):
        dprint('(iter =1)', target, )
        self.setTarget(target.get())
        dprint('(iter =2)', src)
        self.setSrc(src)

    def setTarget(self, vars:list[Var]|Var):
        dprint('> IterAssignExpr setTarget1', vars)
        if not isinstance(vars, list):
            vars = [vars]
        if len(vars) == 1:
            vars = [Var_(), vars[0]]
        self.key = vars[0]
        self.val = vars[1]
        dprint('> IterAssignExpr setTarget2', self.key, self.val)

    def setSrc(self, exp:Expression):
        dprint('> IterAssignExpr setSrc', exp)
        self.srcExpr = exp

    def _start(self, ctx:Context):
        # dprint('#iter-start1 self.srcExpr', self.srcExpr)
        self.srcExpr.do(ctx) # make iter object
        iterSrc = self.srcExpr.get()
        dprint('#iter-start2 itSrc', iterSrc)
        if isinstance(iterSrc, Var):
            iterSrc = iterSrc.get() # extract collection from var
        if isinstance(iterSrc, (ListVal, DictVal)):
            self.itExp = SrcIterator(iterSrc)
        elif isinstance(iterSrc.get(), (NIterator)):
            self.itExp = iterSrc.get()
            
        dprint('#iter-start3 self.itExp', self.itExp)
        self.itExp.start()
        self._first_iter = True
    
    def setIter(self, itExp:NIterator):
        dprint('@# setIter', itExp)
        self.itExp = itExp
    
    def start(self):
        self.itExp.start()
        self._first_iter = True
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        dprint('@# iterAsgn-step', )
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        # print('IterAssignExpr.do', self.itExp, self.key, self.val)
        
        val = self.itExp.get()
        # print('IterAssignExpr.do2 val=', val)
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        k, v = self.key, self.val
        # print('IterAssignExpr.do1 >>>>', k, v)
        if self._first_iter:
            self._first_iter = False
            for vv in [self.key, self.val]:
                # print(' first iter1 >>', vv)
                if not vv or isinstance(vv, Var_):
                    continue
                if isinstance(vv, VarUndefined):
                    vv = Var(vv.name, val.getType())
                # print(' first iter2 >>', vv)
                ctx.addVar(vv)
        # val = self.itExp.get()
        # print('IterAssignExpr.do2 val=', val, val.getType())
        # key = Var_()
        # if isinstance(val, tuple):
        #     key, val = val
        # k, v = self.key, self.val
        # TODO: right way set values to local vars key, val
        # print('IterAssignExpr.do3', key, val)
        # print('IterAssignExpr.do4', k, v)
        if key and not isinstance(key, Var_):
            kvar = Var(k.name, key.getType())
            kvar.set(key)
            ctx.update(k.name, kvar) 
        vvar = Var(v.name, val.getType())
        vvar.set(val)
        ctx.update(v.name, vvar)
        # print('>>> ctx:')
        # ctx.print(forsed=1)


class IndexIterator(NIterator):
    ''' x <- iter(0, 10, 2)'''
    def __init__(self, a, b=None, c=None):
        dprint('IndexIterator:', self, 'a=', a, 'b=', b, 'c=', c)
        # raise DebugExpr('')
        if c is None:
            c = 1
        if b is None:
            b = a
            a = 0
        self.first = a
        self.last = b # not last, but next after last
        self.__step = c
        self.index = a
        self.vtype = TypeIterator()
    
    def start(self):
        self.index = self.first

    def step(self):
        self.index += self.__step

    def hasNext(self):
        return self.index < self.last

    def get(self):
        return Val(self.index, TypeInt())


class SrcIterator(NIterator):
    ''' x <- [10,20,30] '''
    def __init__(self, src:ListVal|DictVal):
        self.src = None
        match src:
            case ListVal():
                self.src = src.elems
            case DictVal():
                self.src = src.data
        # dprint('SrcIterator.__init:', src, self.src)
        self._isDict = isinstance(src, DictVal)
        # self.iterFunc = self._iterList
        self._keys = None
        # if self._isDict:
            # self.iterFunc = self._iterDict
        self.iter = None
        self.vtype = TypeIterator()

    def start(self):
        seq = self.src
        if self._isDict:
            seq = list(seq.keys())
            self._keys = seq
            # self.iterFunc = self._iterDict
        self.iter = IndexIterator(0, len(seq))

    def step(self):
        self.iter.step()
        # self.iterFunc()

    def hasNext(self):
        return self.iter.hasNext()
        
    def get(self):
        key = self.iter.get().get()
        if self._isDict:
            key = self._keys[key]
            val = self.src[key]
            dprint('Iter-dict get: key, val', key, val)
            return (raw2val(key), val)
        return self.src[key]



class ListGenIterator(NIterator, SequenceGen):
    ''' [a..b] from a to b, step |1| 
        TODO: step !?> (-1, 1)
            [1..10 ; 2]
    '''

    def __init__(self, a, b):
        ''' a - begin, 
            b - end '''
        c = 1
        if b < a:
            c *= -1
        self.first = a
        self.last = b # last val
        self.__step = c
        self.val = a
        self.vtype = TypeIterator()

    def start(self):
        self.val = self.first

    def step(self):
        self.val += self.__step

    def hasNext(self):
        return self.val <= self.last

    def get(self):
        return Val(self.val, TypeInt())
    
    def getSlice(self, start, end):
        res = ListVal()
        self.start()
        xlen = int(abs(self.last - self.first) / abs(self.__step)) + 1
        if start < 0:
            start = xlen + start
        if end < 0:
            end = xlen + end
        self.val += start * self.__step
        # TODO: [1:-1]
        maxCount = end
        endVal = self.first + (self.__step * maxCount)
        # print('LG-1: ', self.first, endVal, self.__step, 'base:', self.get())
        while(self.val < endVal and self.hasNext()):
            res.addVal(self.get())
            # print('LGI>>', self.val, ':', res.vals())
            self.step()
            if (self.__step > 0 and self.val >= endVal) or (self.__step < 0 and self.val <= endVal):
                break
        return res
    
    def allVals(self):
        res = ListVal()
        self.start()
        # print('LGI1 (%d, %d)' % (self.first, self.last))
        while(self.hasNext()):
            res.addVal(self.get())
            # print('LGI>>', res.vals())
            self.step()
        return res


class ListGenExpr(Expression):
    ''' [a .. b] '''
    def __init__(self):
        self.iter:NIterator = None
        self.beginExpr = None
        self.endExpr = None

    def setArgs(self, a:Expression, b:Expression):
        self.beginExpr = a
        self.endExpr = b

    def do(self, ctx:Context):
        # dprint('ListGenExpr.do1:', self.beginExpr, self.endExpr)
        self.beginExpr.do(ctx)
        self.endExpr.do(ctx)
        a = self.beginExpr.get()
        b = self.endExpr.get()
        self.iter = ListGenIterator(a.getVal(), b.getVal())
        
    def get(self):
        return Val(self.iter, TypeIterator())
    
    # def vals(self, ctx:Context):
        


class Append(Expression):
    ''' [] <- 12 '''
    
    def __init__(self, left, right):
        super().__init__(None, '')
        self.target:Collection = None
        self.src:Var = None
        if left and right:
            self.setArgs(left, right)

    def setArgs(self, targ:Collection, src:Var|Val):
        dprint('Append setArgs:', targ, src)
        self.target = targ
        self.src = src

    def do(self, ctx:Context):
        # key, val for DictVal. src should be a tuple or dict
        # print('Append do:', self.target, self.src)
        
        if isinstance(self.target, ListVal):
            v = self.src
            val = var2val(v)
            self.target.addVal(val)
        elif isinstance(self.target, DictVal):
            if isinstance(self.src, TupleVal):
                src = self.src.elems
                k, v = src
                key = var2val(k)
                val = var2val(v)
                self.target.setVal(key, val)
            elif isinstance(self.src, DictVal):
                for key, val in self.src.data.items():
                    # print('dd:', key, val)
                    self.target.data[key] = val


class LeftArrowExpr(BinOper):
    ''' '''

    def __init__(self, src = ''):
        super().__init__(None, src)
        self.leftExpr:Expression = None
        self.rightExpr:Expression = None
        self.left:Var|Collection = None
        self.right:Var|NIterator = None
        self.expr = None
        self.isIter = False
        
    def setArgs(self, left, right):
        # print('Arr <- setArgs1', left, right)
        self.leftExpr = left
        self.rightExpr = right

    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.rightExpr.add(expr)
    
    # def start(self, ctx:Context):
    #     self.expr.start()
    
    def init(self, ctx:Context):
        ''' get left, right, decide what the case here: iter or append '''
        # left expression defines type of case
        self.leftExpr.do(ctx)
        # print('..')
        # print('Arr <- init1 ltArg', self.leftExpr)
        ltArg = Var_()
        if isinstance(self.leftExpr, SequenceExpr):
            if self.leftExpr.getDelim() == ',':
                # comma-separated sequence, can interpret as tuple
                # print('Arr <- init011', 'comma-separated sequence')
                # use 2 first vars for key-val of dict
                # TODO: change to multival assignmens
                ltVals = self.leftExpr.getVals(ctx)
                ltArg = ltVals[:2]
        else:
            ltArg  = self.leftExpr.get()
        
        self.rightExpr.do(ctx) # make iter object
        rtArg = self.rightExpr.get()

        # print('Arr <-2 init ltArg', ltArg)
        # print('Arr <-3 init rtArg:', rtArg)
        if isinstance(ltArg, Var) and isinstance(ltArg.getType(), (TypeList, TypeDict)):
            # print('Arr <-2 init ltArg', ltArg.getType())
            ltArg = var2val(ltArg)
        if not isinstance(ltArg, list) and isinstance(ltArg, (ListVal, DictVal)):
            # append case
            if rtArg :
                rtArg = var2val(rtArg)
            self.expr = Append(ltArg, rtArg)
            return

        if isinstance(rtArg, Var):
            rtArg = rtArg.get() # extract collection from var
        # print('Arr <- init4 rtArg:', rtArg)
        itExp = None
        if isinstance(rtArg, (Collection)):
            itExp = SrcIterator(rtArg)
        elif isinstance(rtArg.get(), (NIterator)):
            itExp = rtArg.get()
        
        # print('Arr<- init5 itExp:', itExp)
        if isinstance(itExp, NIterator):
            # iter case
            self.expr = IterAssignExpr()
            self.expr.setTarget(ltArg)
            self.expr.setIter(itExp)
            self.isIter = True
        else:
            raise EvalErr('Undefined case of left-arrow operator (%s <- %s)' % (ltArg, rtArg))
    
    def doCase(self, ctx:Context):
        self.expr.do(ctx)
        if not self.isIter:
            self.expr = None
    
    def do(self, ctx:Context):
        # print('Exp<-do1:', self.expr)
        if self.expr is None:
            self.init(ctx)
        self.doCase(ctx)


class EmptyFilter(Expression):
    def do(self, ctx:Context):
        pass
    
    def get(self) -> Var|list[Var]:
        return Val(True, TypeBool())


class ListComprExpr(Expression):
    '''
    List comprehantion. As possible used haskell-like syntax.
    We don`t use verticall bar (| as haskell) because it olready is used as a bitwise OR with another precedence.
    Semicolon (;) is used for split internal sub-parts instead.
    cases:
    [x ; x <- listVar] # just one-2-one copy Case0
    [ x + 2 ; x <- [a .. b]] # with simple modificator of each element Case1
    [ x ; x <- listVar ; x > 5 ] # with filtering conditions. Last sub-part will be an condition of filter. Case2
    [ x ; x <- listVar ; y, z = x ** 2 , 2 * x ; x + y > 100 && y - z < 1000 ] # with declaration part. Case3
    [x + y ; x <- list1, y <- list2 ; x != y] # several iterators, next in loop of prev. Case3

    Actually comprehantion implements: map, filter (possibly - flat)
    
    [result ; iterator1 ; iteratorN; declarations; filter-condition ]
    
     '''
    def __init__(self):
        super().__init__()
        self.iter:NIterator = None
        self.iterNodes:IterAssignExpr = [] # 1 or more iterators: listVar, [n..m], iter(size)
        self.resExpr = None # result expression, first in parts
        self.declarations:list[list[OpAssign]] = [] # declaration expressions, pre-last part
        self.filter = [] # filter condition, last part
        self.res:ListVal = None # result of comprehansion expression

    def setInner(self, subs:Expression):
        ''' set of expression lists
            1. result-expr
            2. [IterAssignExpr, ... ]
            3. declaration-expr (single assign or multi)
            4. condition-expr
            e.g.:
            x + a ; x <- iter , y <- iter; a = y * 10; a < 100
            x + a ; x <- iter ; x > 2
        '''
        lexp = len(subs)
        if lexp < 2:
            raise InterpretErr(f'Too little subparts of comprehension: {lexp}')
        self.resExpr = subs[0]
        curIt = -1
        for exp in subs[1:]:
            dprint('ListComprExpr.setInner' ,exp, type(exp), 'curIt=', curIt)
            # if isinstance(exp, LeftArrowExpr):
            #     exp.init()
            if isinstance(exp, (LeftArrowExpr,IterAssignExpr)):
                # basic case
                # if curIt > 0 and len(self.filter) == 0:
                #     # fix prev empty filter by True condition
                #     # dprint(' ### EMPTY FILtER for ', curIt)
                #     self.filter[curIt] = EmptyFilter()
                curIt += 1
                self.iterNodes.append(exp)
                self.declarations.append([])
                self.filter.append(EmptyFilter())
            elif curIt > -1 and isinstance(exp, OpAssign):
                # declarations part after iterator
                self.declarations[curIt].append(exp)
            elif curIt > -1:
                # filter condition here. can`t be before iterator`
                self.filter[curIt] = exp

    def doDecl(self, ctx:Context, decl:Expression):
        if len(decl) > 0:
            for dex in decl:
                # updating final context by current declaration expressions
                dprint('$** doDecl', decl)
                # ctx.print()
                dex.do(ctx)

    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        # dprint('COMPRH . doElem. rexpr:', self.resExpr, 'res:', res, 'val:', var2val(res))
        self.res.addVal(var2val(res))
        

    def iterLoop(self, index, ctx:Context):
        dprint('ListComprExpr.iterLoop %d of %d ' % (index, len(self.iterNodes)), self.iterNodes)
        q='''
        [a, b, c] ; a <- aaa; a > 10;    b <- bbb; c = a + b;  b > 20;   
        '''
        inod:IterAssignExpr|LeftArrowExpr = self.iterNodes[index]
        
        if isinstance(inod, LeftArrowExpr):
            inod.init(ctx)
            inod = inod.expr
            inod.start()
        decl = self.declarations[index]
        filt = self.filter[index]
        dprint(' $$ 1',)
        # ctx.print()
        while inod.cond():
            subCtx = Context(ctx) # ctx for sub-iter
            inod.do(subCtx) # make iterator
            self.doDecl(subCtx, decl)
            # dprint('iterLoop.. filt:', self.filter, index)
            dprint(' $$ 2 ',)
            # subCtx.print()
            filt.do(subCtx)
            fcond = filt.get().get()
            if fcond:  
                if index + 1 < len(self.iterNodes):
                    # continue dive into iterators chainfilt
                    self.iterLoop(index + 1, subCtx)
                else:
                    # eval elem result expression
                    self.doElem(subCtx)
            inod.step()

    def do(self, ctx:Context):
        dprint('ListComprExpr.do0')
        self.res = ListVal()
        if len(self.iterNodes) == 0:
            return
        self.iterLoop(0, ctx)

    def get(self):
        return self.res
    


