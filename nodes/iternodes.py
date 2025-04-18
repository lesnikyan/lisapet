
'''
Iteration expressions.
Mostly for usage into for-loop or generators.
'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.oper_nodes import OpAssign
from nodes.func_expr import FuncCallExpr
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
        print('(iter =1)', target, )
        self.setTarget(target.get())
        print('(iter =2)', src)
        self.setSrc(src)

    def setTarget(self, vars:list[Var]|Var):
        print('> IterAssignExpr setTarget1', vars)
        if not isinstance(vars, list):
            vars = [vars]
        if len(vars) == 1:
            vars = [Var_(), vars[0]]
        self.key = vars[0]
        self.val = vars[1]
        print('> IterAssignExpr setTarget2', self.key, self.val)

    def setSrc(self, exp:Expression):
        print('> IterAssignExpr setSrc', exp)
        self.srcExpr = exp

    def _start(self, ctx:Context):
        # print('#iter-start1 self.srcExpr', self.srcExpr)
        self.srcExpr.do(ctx) # make iter object
        iterSrc = self.srcExpr.get()
        print('#iter-start2 itSrc', iterSrc)
        if isinstance(iterSrc, Var):
            iterSrc = iterSrc.get() # extract collection from var
        if isinstance(iterSrc, (ListVal, DictVal)):
            self.itExp = SrcIterator(iterSrc)
        elif isinstance(iterSrc.get(), (NIterator)):
            self.itExp = iterSrc.get()
            
        print('#iter-start3 self.itExp', self.itExp)
        self.itExp.start()
        self._first_iter = True
    
    def setIter(self, itExp:NIterator):
        print('@# setIter', itExp)
        self.itExp = itExp
    
    def start(self):
        self.itExp.start()
        self._first_iter = True
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        print('@# iterAsgn-step', )
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        print('IterAssignExpr.do', self.itExp)
        if self._first_iter:
            print('IterAssignExpr.do1 >>>>')
            self._first_iter = False
            for vv in [self.key, self.val]:
                print(' first iter >>', vv)
                if not vv or isinstance(vv, Var_):
                    continue
                ctx.addVar(vv)
        val = self.itExp.get()
        print('IterAssignExpr.do2', val)
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        k, v = self.key, self.val
        # TODO: right way set values to local vars key, val
        # print('IterAssignExpr.do2', key, val)
        if key and not isinstance(key, Var_):
            ctx.update(k.name, key)
        ctx.update(v.name, val)


class IndexIterator(NIterator):
    ''' x <- iter(0, 10, 2)'''
    def __init__(self, a, b=None, c=None):
        print('IndexIterator:', self, 'a=', a, 'b=', b, 'c=', c)
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
        return Val(self.index, TypeInt)


class SrcIterator(NIterator):
    ''' x <- [10,20,30] '''
    def __init__(self, src:list|dict):
        self.src = src.elems
        # self.iterFunc = self._iterList
        self._isDict = isinstance(self.src, dict)
        self._keys = None
        # if self._isDict:
            # self.iterFunc = self._iterDict
        self.iter = None
        self.vtype = TypeIterator()

    def start(self):
        seq = self.src
        if self._isDict:
            seq = seq.keys()
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
        return self.src[key]


class ListGenIterator(NIterator):
    ''' [a..b] from a to b, step |1| '''

    def __init__(self, a, b):
        ''' a - begin, 
            b - end '''
        c = 1
        if b < a:
            c = -1
        self.first = a
        self.last = b # last val
        self.__step = c
        self.index = a
        self.vtype = TypeIterator()
    
    def start(self):
        self.index = self.first

    def step(self):
        self.index += self.__step

    def hasNext(self):
        return self.index <= self.last

    def get(self):
        return Val(self.index, TypeInt)


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
        self.beginExpr.do(ctx)
        self.endExpr.do(ctx)
        a = self.beginExpr.get()
        b = self.endExpr.get()
        self.iter = ListGenIterator(a.getVal(), b.getVal())
        
    def get(self):
        return Val(self.iter, TypeIterator())


class Append(Expression):
    ''' [] <- 12 '''
    
    def __init__(self, left, right):
        super().__init__(None, '')
        self.target:Collection = None
        self.src:Var = None
        if left and right:
            self.setArgs(left, right)

    def setArgs(self, targ:Collection, src:Var|Val):
        print('Append setArgs:', targ, src)
        self.target = targ
        self.src = src

    def do(self, ctx:Context):
        # key, val for DictVal. src should be a tuple
        print('Append do:', self.target, self.src)
        key, val = None, None
        if isinstance(self.src, TupleVal):
            src = self.src.elems
            k, v = src
            key = var2val(k)
        else:
            v = self.src
        val = var2val(v)
        
        if isinstance(self.target, ListVal):
            self.target.addVal(val)
        elif isinstance(self.target, DictVal):
            self.target.setVal(key, val)


class LeftArrowExpr(Expression):
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
        self.leftExpr = left
        self.rightExpr = right
    
    # def start(self, ctx:Context):
    #     self.expr.start()
        
    
    def init(self, ctx:Context):
        ''' get left, right, decide what the case here: iter or append '''
        # left expression defines type of case
        self.leftExpr.do(ctx)
        ltArg  = self.leftExpr.get()
        
        self.rightExpr.do(ctx) # make iter object
        rtArg = self.rightExpr.get()

        print('Arr <-2 ltArg', ltArg)
        print('Arr <-3 rtArg:', rtArg)
        if isinstance(ltArg.get(), Collection):
            # append case
            self.expr = Append(ltArg.get(), rtArg)
        else:
            if isinstance(rtArg, Var):
                rtArg = rtArg.get() # extract collection from var
            print('Arr <-4 rtArg:', rtArg)
            itExp = None
            if isinstance(rtArg, (Collection)):
                itExp = SrcIterator(rtArg)
            elif isinstance(rtArg.get(), (NIterator)):
                itExp = rtArg.get()
            
            print('Arr<-5 itExp:', itExp)
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
        print('Exp<-do1:', self.expr)
        if self.expr is None:
            self.init(ctx)
        self.doCase(ctx)


class EmptyFilter(Expression):
    def do(self, ctx:Context):
        pass
    
    def get(self) -> Var|list[Var]:
        return Val(True, TypeBool)


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
        self.res:ListVal = ListVal() # result of comprehansion expression

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
            print('ListComprExpr.setInner' ,exp, type(exp), 'curIt=', curIt)
            # if isinstance(exp, LeftArrowExpr):
            #     exp.init()
            if isinstance(exp, (LeftArrowExpr,IterAssignExpr)):
                # basic case
                if curIt > 0 and len(self.filter[curIt]) == 0:
                    # fix prev empty filter by True condition
                    # print(' ### EMPTY FILtER for ', curIt)
                    self.filter[curIt] = EmptyFilter()
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
                print('$** doDecl', decl)
                # ctx.print()
                dex.do(ctx)

    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        # print('COMPRH . doElem. rexpr:', self.resExpr, 'res:', res)
        self.res.addVal(res)
        

    def iterLoop(self, index, ctx:Context):
        print('ListComprExpr.iterLoop %d of %d ' % (index, len(self.iterNodes)), self.iterNodes)
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
        print(' $$ 1',)
        ctx.print()
        while inod.cond():
            subCtx = Context(ctx) # ctx for sub-iter
            inod.do(subCtx) # make iterator
            self.doDecl(subCtx, decl)
            # print('iterLoop.. filt:', self.filter, index)
            print(' $$ 2 ',)
            subCtx.print()
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
        print('ListComprExpr.do0')
        if len(self.iterNodes) == 0:
            return
        self.iterLoop(0, ctx)

    def get(self):
        return self.res
    


