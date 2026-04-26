
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
    
    def __init__(self):
        self.vtype = TypeIterator()
    
    def getType(self):
        return self.vtype
    
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
        self.itExp:NIterator = None # right part, iterator
        self.srcExpr:CollectionExpr = None # right part, collection constructor, func(), var
        self.loopVars = []
        self._first_iter = False

    def setArgs(self, target, src):
        # print('setArgs', target, , src)
        self.setTarget(target.get())
        self.setSrc(src)

    def setTarget(self, vars:list[Var]|Var):
        # print('> IterAssignExpr setTarget1', vars)
        if not isinstance(vars, list):
            vars = [vars]
        if len(vars) == 1:
            vars = [vars[0]]
        self.loopVars = vars

    def setSrc(self, exp:Expression):
        self.srcExpr = exp

    # def _start(self, ctx:Context):
    #     self.srcExpr.do(ctx) # make iter object
    #     iterSrc = self.srcExpr.get()
    #     if isinstance(iterSrc, Var):
    #         iterSrc = iterSrc.get() # extract collection from var
    #     if isinstance(iterSrc, (ListVal, DictVal)):
    #         self.itExp = SrcIterator(iterSrc)
    #     elif isinstance(iterSrc.get(), (NIterator)):
    #         self.itExp = iterSrc.get()
            
    #     self.itExp.start()
    #     self._first_iter = True
    
    def setIter(self, itExp:NIterator):
        # print('@# setIter', itExp)
        self.itExp = itExp
    
    def start(self):
        self.itExp.start()
        self._first_iter = True
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        # dprint('@# iterAsgn-step', )
        self.itExp.step()
    
    def varsInit(self, ctx):
        self._first_iter = False
        for vv in self.loopVars:
            # print(' first iter1 >>', vv)
            if not vv or isinstance(vv, Var_):
                continue
            if isinstance(vv, VarUndefined):
                vv = Var(vv.name, TypeAny())
            # print(' first iter2 >>', vv)
            ctx.addVar(vv)
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        
        if self._first_iter:
            self.varsInit(ctx)
        # print('IterAssignExpr.do', self.itExp, self.key, self.val)
        # import time
        # time.sleep(1)
        val = self.itExp.get()
        # print('IterAssignExpr.do2 val=', self.itExp, val)
        valSet = []
        
        largLen = len(self.loopVars)
        
        if isinstance(val, (TupleVal, ListVal)):
            valSet = val.elems
        elif isinstance(val, (list)):
            # multi-source case
            valSet = val
        
        
        if largLen == 1:
            if isinstance(val, tuple):
                # dict elem, convert to TupleVal
                valSet = TupleVal(elems=[n for n in val])
            else:
                # whole data into 1 var
                valSet = val
            valSet = [valSet]
        elif largLen == 2 and isinstance(val, tuple):
            # dict elem here, need to unpack
            valSet = val
        # else:
            # print('valSet', valSet)
        

        vlen = len(valSet)
        # print('ind$1>>', vlen, valSet)
        if vlen != largLen:
            raise EvalErr(f"Arrow assign has different left {largLen} and right {vlen} count of elements.")

        for i in range(largLen):
            arg = self.loopVars[i]
            if isinstance(arg, Var_):
                continue
            elem = valSet[i]
            # print('for <- arg, val', i , '>>', arg,  elem)
            varName = arg.name
            nvar = Var(varName, elem.getType())
            nvar.set(elem)
            ctx.update(varName, nvar)

class IndexIterator(NIterator):
    ''' x <- iter(0, 10, 2)'''
    def __init__(self, a, b=None, c=None):
        # print('IndexIterator:',  'a=', a, 'b=', b, 'c=', c)
        # raise DebugExpr('')
        if c is None:
            c = 1
        if b is None:
            b = a
            a = 0
        self.first = a
        self.__step = c
        self.index = a
        self.k = 1
        if self.__step < 0:
            self.k = -1
        self.last = b * self.k # not last, but next to last, depending of step
        self.vtype = TypeIterator()

    def start(self):
        self.index = self.first

    def step(self):
        # print('IndexIterator.step', self.index, '+=', self.__step)
        self.index += self.__step

    def hasNext(self):
        # cur = self.index
        # fin = self.last
        # df = fin - cur
        # k = 1 if self.__step > 0 else -1
        # print('IIt.nest?:', self.index, '*', self.k , '<', self.last)
        return self.index * self.k < self.last

    def get(self):
        return Val(self.index, TypeInt())


class SrcIterator(NIterator):
    ''' x <- [10,20,30] 
        k, v <- {1:11, 2:22}
        x, y, z <- [1, 2], [3,4], (5,6)
    '''
    
    def __init__(self, src:ListVal|DictVal|TupleVal=None):
        self.src = None
        self.iter = None
        self.vtype = TypeIterator()
        if not src:
            return
        match src:
            case BytesVal() | StringVal():
                self.src = src.val
            # case StringVal():
            #     self.src
            case ListVal() | TupleVal():
                self.src = src.elems
            case DictVal():
                self.src = src.data
            case _ if src:
                self.src = src
        # print('SrcIterator.__init:', src, self.src)
        self._isDict = isinstance(src, DictVal)
        self._keys = None

    def start(self):
        seq = self.src
        # print('for n <- m / 1', self, seq)
        if self._isDict:
            seq = list(seq.keys())
            self._keys = seq
        self.iter = IndexIterator(0, len(seq))

    def step(self):
        self.iter.step()

    def hasNext(self):
        return self.iter.hasNext()
        
    def get(self):
        key = self.iter.get().get()
        if self._isDict:
            key = self._keys[key]
            val = self.src[key]
            # dprint('Iter-dict get: key, val', key, val)
            return (raw2val(key), val)
        val = self.src[key]
        # print('IterSrc.get:', val)
        if isinstance(self.src, bytearray):
            val = Val(val, TypeInt())
        elif isinstance(self.src, str):
            val = Val(Glif(val), TypeGlif())
        return val


class MultiSrcIterator(SrcIterator):
    
    def __init__(self, src:list):
        super().__init__(None)
        self.sources:list[NIterator] = []
        self.initSrc(src)
        
    def initSrc(self, srcSet:list):
        for src in srcSet:
            if not isinstance(src, NIterator):
                # print('MSIt,init', src)
                src = SrcIterator(src)
            self.sources.append(src)
    
    def start(self):
        ''''''
        for srs in self.sources:
            srs.start()
        

    def step(self):
        for srs in self.sources:
            srs.step()
    
    def hasNext(self):
        ''' Iter count by 1-st sub-source '''
        return self.sources[0].hasNext()


    def get(self):
        res = []
        for srs in self.sources:
            r = srs.get()
            if isinstance(r, tuple):
                res.extend(r)
            else:
                res.append(r)
        return res


class GenIterator(NIterator, SequenceGen):
    ''' '''


class ListGenIterator(GenIterator):
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
    
    def len(self):
        return int(abs(self.last - self.first) / abs(self.__step)) + 1
    
    def getSlice(self, start, end):
        res = ListVal()
        self.start()
        xlen = self.len()
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
    
    def makeElems(self):
        ''' method for internal usage, avoid to make unnecessary ListVal '''
        res = []
        self.start()
        # print('LGI1 (%d, %d)' % (self.first, self.last))
        while(self.hasNext()):
            res.append(self.get())
            self.step()
        return res
    
    def allVals(self):
        elems = self.makeElems()
        res = ListVal(elems = elems)
        return res


class TwoDotsOper(Expression):
    ''' a .. b 
        Abstract binary operator
        usage:
        inner espression in List generator
    '''
    def __init__(self):
        self.iter:NIterator = None
        self.beginExpr = None
        self.endExpr = None

    def setArgs(self, a:Expression, b:Expression):
        self.beginExpr = a
        self.endExpr = b

    def getListGen(self):
        expr = ListGenExpr()
        expr.setArgs(self.beginExpr, self.endExpr)
        return expr


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


class Append(Expression):
    ''' [] <- 12 '''
    
    def __init__(self, left, right):
        super().__init__(None, '')
        self.target:Collection = None
        self.src:Var = None
        if left and right:
            self.setArgs(left, right)

    def setArgs(self, targ:Collection, src:Var|Val):
        # print('Append setArgs:', targ, src)
        self.target = targ
        self.src = src

    def do(self, ctx:Context):
        # key, val for DictVal. src should be a tuple or dict
        # print('Append do:', self.target, self.src)
        
        if isinstance(self.target, (ListVal, BytesVal)):
            v = self.src
            val = var2val(v)
            # print('$4 ', v, val)
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
    ''' a <- b '''

    def __init__(self, src = ''):
        super().__init__(None, src)
        self.leftExpr:Expression = None
        self.rightExpr:Expression = None
        self.left:Var|Collection = None
        self.right:Var|NIterator = None
        self.expr = None
        self.isIter = False
        self.isAssign = None
        
    def setArgs(self, left, right):
        # print('Arr <- setArgs1', left, right)
        self.leftExpr = left
        self.rightExpr = right

    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.rightExpr.add(expr)
    
    def setAssign(self):
        self.isAssign = True
    
    # def start(self, ctx:Context):
    #     self.expr.start()
    
    def init(self, ctx:Context):
        ''' get left, right, decide what the case here: iter or append '''
        # left expression defines type of case
        varParent = ctx
        # make
        # if self.isAssign:
        #     varParent = None
        varCtx = Context(varParent)
            
        self.leftExpr.do(varCtx)
        # print('..')
        # print('Arr <- init1', self.leftExpr, '<-', self.rightExpr)
        ltArg = None
        rtArg = None
        if isinstance(self.leftExpr, SequenceExpr):
            if self.leftExpr.getDelim() == ',':
                # comma-separated sequence, can interpret as a tuple
                # print('Arr <- init011', 'comma-separated sequence')
                # deprecate:  use 2 first vars for key-val of dict
                # 1 var for list - value for elem from list/tuple
                # 2 for dict - key,val
                # 1 for dict - tuple (key, val) to assign 
                # 2 or more for list - unpack current elem into vars [(,,), (,,)]
                ltVals = self.leftExpr.getVals(varCtx)
                ltArg = ltVals
        else:
            ltArg  = self.leftExpr.get()
        
        self.rightExpr.do(ctx) # make iter object
        # print('Arr <- do3', self.leftExpr, '<-', self.rightExpr)
        
        if isinstance(self.rightExpr, SequenceExpr):
            if self.rightExpr.getDelim() == ',':
                rtArg = self.rightExpr.getVals(ctx)
        else:
            rtArg = self.rightExpr.get()

        # print('Arr <-2 init ltArg', ltArg, ltArg.__class__)
        # print(' <- init rtArg:', rtArg)
        
        # try check append
        if not self.isAssign:
            if isinstance(ltArg, Var) and isinstance(ltArg.getType(), (TypeList, TypeDict, TypeBytes)):
                ltArg = var2val(ltArg)
                
            # print('Arr <-4 init ltArg', ltArg, ltArg.__class__)
            
            # Found: append case: ListVal|DictVal|BytesVal <- val
            if isinstance(ltArg, (ListVal, DictVal, BytesVal)):
                if rtArg :
                    rtArg = var2val(rtArg)
                self.expr = Append(ltArg, rtArg)
                return

        # Found: iteration assign case
        rtSet = None
        if isinstance(rtArg, Var):
            rtArg = rtArg.get() # extract collection from var
        elif isinstance(rtArg, list):
            # multi-source
            # print('rtArg:', rtArg)
            rtSet = []
            for rarg in rtArg:
                # print('rarg:', rarg, rarg.get(), rarg.getType())
                rarg = var2val(rarg)
                if isinstance(rarg, (ListVal, TupleVal, DictVal)):
                    pass # already valid operand
                elif isinstance(rarg, Val):
                    rarg = rarg.get()
                rtSet.append(rarg)
        
        # print('rtSet', rtSet)
        # print('Arr <- init4 rtArg:', rtArg)
        # print('Arr <- init4 ltArg:', ltArg)
        itExp = None
        if isinstance(rtArg, (Collection, BytesVal, StringVal)):
            itExp = SrcIterator(rtArg)
        elif rtSet:
            itExp = MultiSrcIterator(rtSet)
        elif isinstance(rtArg.get(), (NIterator)):
            itExp = rtArg.get()
        
        # print('Arr<- init5 ltArg, rtArg:', ltArg, rtArg)
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


# ComprehensionExpr
class ComprehensionGen(Expression):
    ''' Base functionality of comprehension generator.
        This class can't be used as is.
        Methods `resultObject`, `doElem` should be implemented for each final case
    '''
    
    def __init__(self):
        super().__init__()
        self.iter:NIterator = None
        self.iterNodes:IterAssignExpr = [] # 1 or more iterators: listVar, [n..m], iter(size)
        self.resExpr = None # result expression, first in parts
        self.declarations:list[list[OpAssign]] = [] # declaration expressions, pre-last part
        self.filter = [] # filter condition, last part
        self.res = None
    
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
            # print('ComprExpr.setInner' ,exp, type(exp), 'curIt=', curIt)
            if isinstance(exp, (LeftArrowExpr,IterAssignExpr)):
                # basic case
                curIt += 1
                exp.setAssign()
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
                # dprint('$** doDecl', decl)
                # ctx.print()
                dex.do(ctx)

    def resultObject(self) -> Collection:
        ''' result instance: ListVal, DictVal, etc '''

    def doElem(self, ctx:Context):
        '''result-related method'''

    def iterLoop(self, index, ctx:Context):
        # print('ListComprExpr.iterLoop %d of %d ' % (index, len(self.iterNodes)), self.iterNodes)
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
        # print(' $$ 1',)
        # ctx.print()
        while inod.cond():
            subCtx = Context(ctx) # ctx for sub-iter
            inod.do(subCtx) # make iterator
            self.doDecl(subCtx, decl)
            # print('iterLoop.. filt:', self.filter, index)
            # print(' $$ 2 ',)
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

    def fin(self):
        pass

    def do(self, ctx:Context):
        # print('ListComprExpr.do0', self.iter)
        
        self.res = None # reset prev
        self.resultObject()
        if len(self.iterNodes) == 0:
            return
        self.iterLoop(0, ctx)
        self.fin()

    def get(self):
        return self.res
    


class ListComprExpr(ComprehensionGen):
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
        self.res:ListVal = None

    def resultObject(self):
        ''' '''
        self.res = ListVal()
    
    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        # print('L-COMPRH . doElem. rexpr:', self.resExpr, 'res:', res, 'val:', var2val(res))
        self.res.addVal(var2val(res))
    

class DictComprExpr(ComprehensionGen):
    '''
        {k:v ; k, v <- src; assign? ; cond}
    '''
    def __init__(self):
        super().__init__()
        self.resExpr:ServPairExpr
        self.res:DictVal = None

    def resultObject(self):
        ''' '''
        self.res = DictVal()
    
    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        k, v = self.resExpr.get()
        key = var2val(k)
        val = var2val(v)
        # print('D-COMPRH . doElem. rexpr:', self.resExpr, 'res:', k,v) #  'val:', var2val(res)
        self.res.setVal(key, val)
    

class BytesComprExpr(ComprehensionGen):
    '''
        0x[n ; n <- src; assign? ; cond]
    '''
    def __init__(self):
        super().__init__()
        self.resExpr:Expression
        self.res:BytesVal = None

    def resultObject(self):
        ''' '''
        self.res = BytesVal()
    
    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        # print('B-COMPRH . doElem. rexpr:', self.resExpr, 'res:', res, 'val:', var2val(res))
        self.res.addVal(var2val(res))


class StringComprExpr(ComprehensionGen):
    '''
        ~[s ; s <- src; assign? ; cond]
    '''
    def __init__(self):
        super().__init__()
        self.resExpr:Expression
        self.vals = []
        self.res:StringVal = None

    def resultObject(self):
        ''' '''
        self.res = None
        self.vals = []
    
    def fin(self):
        self.res = StringVal(''.join(self.vals))
    
    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        rv = var2val(res).getVal()
        # print('B-COMPRH . doElem. rexpr:', self.resExpr, 'res:', res, 'val:', rv)
        if isinstance(rv, Glif):
            rv = rv.val
        self.vals.append(rv)


class GenSubNode(Expression):
    def __init__(self, iter=None, src=None):
        super().__init__(None, src=src)
        self.finished = True

    def start(self):
        pass
    
    def do(self, ctx=None):
        pass
    
    def cond(self):
        return True
    
    def hasNext(self):
        return False
    
    def step(self):
        return True


class SubIterNode(GenSubNode):
    ''' one section in generator (iter ; assign ; cond) '''

    debid = 1
        
    def __init__(self, iter=None, src=None):
        super().__init__(None, src=src)
        self.did = SubIterNode.debid # debug id
        SubIterNode.debid += 1
        self._origIter = iter
        self.iter:IterAssignExpr = iter
        self.ctx:Context = None
        self.subExprs:list[Expression] = []
        self.ifcond:Expression = None
        self.finished = True
        self.subNode:SubIterNode = None
    
    def addSub(self, sub:Expression):
        self.subExprs.append(sub)
    
    def setSubNode(self, sub:Expression):
        self.subNode = sub
    
    def setCond(self, cond:Expression):
        self.ifcond = cond
    
    def setContext(self, ctx:Context):
        self.ctx = ctx
    
    def start(self):
        self._origIter = self.iter
        self.finished = False
        subCtx = self.ctx
        if isinstance(self._origIter, LeftArrowExpr):
            # print(f'\nsubNode.start<{self.did}> iter', f'<={self.did}>', self._origIter)
            self._origIter.setAssign()
            self._origIter.init(subCtx)
            # if isinstance(self._origIter.expr, IterAssignExpr):
            self.iter = self._origIter.expr
        # print('subNode iter2', self.iter)
        # self.iter.init(self.ctx)
        self.iter.start()
        self.do()
        cval = self.ifcond.get()
        ifres = var2val(cval).get()
        
        if not ifres:
            sres = self.step(curOnly=True)
            if not sres:
                return False
        if self.subNode:
            stres = self.subNode.start()
            if not stres:
                return self.step()
        return True
            # if not self.subNode.cond()
    
    def doSubs(self):
        for exp in self.subExprs:
            exp.do(self.ctx)
    
    def do(self, ctx=None):
        # self._origIter.do(self.ctx)
        self.iter.do(self.ctx)
        self.doSubs()
        self.ifcond.do(self.ctx)
        # print(f'sind<{self.did}>.',  'do:', self.ctx.vars)
    
    def hasNext(self):
        if self.finished:
            return False
        return self.iter.cond()
    
    def cond(self):
        cval = self.ifcond.get() # Val(true) # valid condition -> stop loop
        # print(f'?? subInod<{self.did}>.cond:', var2val(cval).get())
        return var2val(cval).get()
        
    
    # def _step(self):
    #     # print('subNode.step')
    #     self.iter.step()
    #     # print('$11', f'?<?{self.did}>', 'if:', self.iter.cond(), self.finished)
    #     if self.finished:
    #         return False
    #     while self.iter.cond(): # has next
    #         # print('$12')
    #         self.do()
    #         cval = self.ifcond.get()
    #         ifres = var2val(cval).get()
            
    #         ccx = self.ctx
    #         vvs = []
    #         while ccx.upper:
    #             vv = [(k, v.getVal()) for k, v in self.ctx.vars.items() if not isinstance(v.getType(), (TypeList, TypeGenerator ))]
    #             vvs.append(vv)
    #         # vv = [(k, v.getVal()) for k, v in self.ctx.vars.items() if not isinstance(v.getType(), (TypeList, TypeGenerator ))]
    #         # vu = [(k, v.getVal()) for k, v in self.ctx.upper.vars.items() if not isinstance(v.getType(), (TypeList, TypeGenerator ))]
    #         # print('ssubNd.step2<', self.did, 'vrs:', vv, vu, '>', self.ifcond, expSrc(self.ifcond),  cval, ifres)
    #         if ifres:
    #             return True # correct condition has reached
    #         self.iter.step()
    #         # print('ino.step w-end:', self.iter.cond())
    #     # print('inod step.False')
    #     self.finished = True
    #     return False # iter ended without result
    
    def debVV(self):
            ccx = self.ctx
            vvs = []
            while ccx.upper is not None:
                vv = [(k, v.getVal()) for k, v in ccx.vars.items() if not isinstance(v.getType(), (TypeList, TypeGenerator ))]
                vvs.append(vv)
                ccx = ccx.upper
            return vvs
    
    def step(self, curOnly=False):
        # print(f'~~step <{self.did}>')
        if not curOnly and self.subNode and not self.subNode.finished:
            ss = self.subNode.step()
            if ss:
                return True
        # print(f'vv$1<{self.did}>:', expSrc(self.ifcond), self.debVV())
        self.iter.step()
        # print('$$ i.cond:', self.iter.cond())
        while self.iter.cond():
            # subNode has finished
            self.do()
            # print(f'vv$2<{self.did}>:', expSrc(self.ifcond), self.debVV())
            cval = self.ifcond.get()
            ifres = var2val(cval).get()
            if not ifres:
                self.iter.step()
                continue
            if curOnly or not self.subNode:
                return True
            if not self.subNode.start():
                self.iter.step()
                continue
            if self.subNode.cond():
                # print('sind.step$5', self.subNode.cond())
                return True
            self.iter.step()
        # print(f'last step {self.did}')
        return False


# SequenceGenerator
class InlineGen(GenIterator):
    '''
    Generator returned from expression:
    (: n ; n <- src)
    '''
    
    def __init__(self):
        super().__init__()
        self.vtype = TypeGenerator()
        self.ctx:Context = None
        self.deepCtx:Context = None
        self.resExpr = None # result expression, first in parts
        self.continued = False
        self.root = None
        self.lastInode = None
    
    def getType(self):
        return self.vtype

    def addIter(self, iterNode:SubIterNode):
        if self.root is None:
            self.root = iterNode
            self.lastInode = iterNode
            return
        self.lastInode.setSubNode(iterNode)
        self.lastInode = iterNode
        
    def hasNext(self):
        ''' if not last position '''
        return self.continued
    
    def doElem(self, ctx:Context):
        self.resExpr.do(ctx)
        res = self.resExpr.get()
        return var2val(res)

    def get(self):
        ''' get current element '''
        if not self.continued:
            raise EvalErr('LIterGenerator.incorrect get after stop')
        deepCtx = self.lastInode.ctx
        return self.doElem(deepCtx)

    def start(self):
        self.continued = True
        self.root.start()

    def _stop(self):
        self.continued = False
        return False

    def step(self):
        rst = self.root.step()
        if not rst:
            self._stop()


class InlineGenExpr(GenIterator):
    ''' expression like (: ; ; )
    '''
    
    def __init__(self):
        super().__init__()
        self.ingen:InlineGen = None
        self.subs = []
        self.res = None
    
    def get(self):
        return self.res
    
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
        self.subs = subs
    
    def makeGen(self, ctx:Context):
        self.ingen = InlineGen()
        lexp = len(self.subs)
        if lexp < 2:
            raise InterpretErr(f'Too little subparts of comprehension: {lexp}')
        self.ingen.resExpr = self.subs[0]
        curIt = -1
        curInode = None
        subCtx = ctx
        for exp in self.subs[1:]:
            if isinstance(exp, (LeftArrowExpr,IterAssignExpr)):
                # basic case
                curIt += 1
                exp.setAssign()
                curInode = SubIterNode(exp)
                subCtx = Context(subCtx)
                curInode.setContext(subCtx)
                self.ingen.addIter(curInode)
                curInode.setCond(EmptyFilter())
            elif curIt > -1 and isinstance(exp, OpAssign):
                # declaration|assign part after iterator
                curInode.addSub(exp)
            elif curIt > -1:
                # filter condition here. can`t be before iterator`
                curInode.setCond(exp)

    def do(self, ctx:Context):
        self.makeGen(ctx)
        self.res = Val(self.ingen, TypeGenerator())
        


