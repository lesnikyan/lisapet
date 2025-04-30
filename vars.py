'''
Var types
'''

from lang import *
from base import *
from typex import *


class TypeVal(Val):
    def __init__(self, val:VType):
        super().__init__(val, TypeType)


class Var_(Var):
    ''' expr: _ '''
    name = '_'
    def __init__(self):
        self.vtype:VType = TypeNull
        self.val = None


class VarUndefined(Var):
    def __init__(self, name):
        super().__init__(name, Undefined)


class VarNull(Var):
    ''' None|null'''

    def __init__(self, name=None):
        super().__init__(name, TypeNull)

    def setType(self, t:VType):
        pass


def value(val, vtype:VType)->Val:
    return Val(val, vtype)

# type: Comparable, Container, Numeric 

class CompVar(Var):
    def compare(self, other:'CompVar')-> int:
        a, b = self.get(), other.get()
        if a == b:
            return 0
        return a - b


class VarRatio(CompVar):
    def __init__(self, a:int, b:int, name=None):
        super().__init__(name, TypeRatio)
        self.numer:int = a # numerator
        self.denom:int = b # denominator

    def float(self):
        return Val(self.numer / self.denom, TypeFloat())


class FuncRes(Val):
    ''' '''
    def __init__(self, val):
        super().__init__(val, TypeAny())

# Collections


class Collection(Container):

    def setVal(self, key:Var, val:Var):
        pass

    def getVal(self, key:Var):
        pass
    
    def len(self)->int:
        return 0

    def vals(self):
        pass


class ListVal(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, **kw):
        super().__init__(None, TypeList())
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Val] = ees

    def len(self)->int:
        return len(self.elems)
    
    def addVal(self, val:Val):
        # not sure, we need whole Var or just internal value?
        print('ListVal.addVal:', val)
        self.elems.append(val)
    
    def setVal(self, key:Val, val:Val):
        i = key.getVal()
        # print('ListVar.setVal', i, val, 'Len=', len(self.elems), i < len(self.elems), self.elems)
        if i >= len(self.elems):
            raise EvalErr('List out of range by index %d ' % i)
        self.elems[i] = val

    def getVal(self, key:Val|int):
        print('ListVal.getVal1, index:', key)
        # print('ListVal.getVal1, elems:', self.elems)
        i = key
        # if isinstance(key, Val):
        #     i = key.get()
        i = key.getVal()
        print('@ i=', i)
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('List out of range by index %d ' % i)

    def getSlice(self, beg, end):
        if beg < 0 or end > len(self.elems):
            raise EvalErr('indexes of List slice are out of range [%d : %d] with len = %d' % (beg, end, len(self.elems)))
        rdata = self.elems[beg: end]
        return ListVal(elems=rdata)

    def get(self):
        return  [n.get() for n in self.elems] # debug
        # return self.elems

    def vals(self):
        return [(n.get()) for n in self.elems[:10]]

    def rawVals(self):
        return [n for n in self.elems[:]]

    def __str__(self):
        # nm = self.name
        # if not nm:
            # nm = '#list-noname'
        def strv(var):
            # print('@>>', var, var.getType(),  isinstance(var.getType(), TypeContainer), ' str:', str(var))
            if isinstance(var.getType(), TypeContainer):
                return str(var)
            return str(var.get())
        vals = [strv(n) for n in self.elems[:10]]
        return 'ListVal([%s])' % (', '.join(vals))


class TupleVal(Collection):
    ''' '''
    def __init__(self, **kw):
        super().__init__(None, TypeTuple())
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Val] = ees

    def len(self)->int:
        return len(self.elems)
    
    def get(self):
        return tuple([n.get() for n in self.elems])
        # return tuple(self.elems)

    def addVal(self, val:Val):
        self.elems.append(val)

    def getVal(self, key:Val|int):
        # i = key
        # if isinstance(key, Val):
        #     i = key.get()
        i = key.getVal()
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('Tuple out of range by index %d ' % i)

    def __str__(self):
        vals = ', '.join([ '%s' % n.get() for n in self.elems])
        return 'TupleVal(%s)' %  (vals)


class DictVal(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, name=None):
        super().__init__(None, TypeDict())
        self.data:dict[str|int|bool,Val] = {}

    def len(self)->int:
        return len(self.data)
        
    def inKey(self, key:Var)->str:
        return '%s__%s' % (key.get(), key.getType().__class__.__name__)

    def setVal(self, key:Val, val:Val):
        # k = self.inKey(key)
        self.data[key.get()] = val

    def getKeys(self):
        # res = [ListVar(k) for k in self.data]
        res = ListVal()
        for k in self.data:
            res.addVal(k)
        return res

    def getVal(self, key:Val):
        # k = self.inKey(key)
        k = key.getVal()
        if k in self.data:
            return self.data[k]
        raise EvalErr('List out of range by key %s ' % k)

    def vals(self):
        return {k: v.get() for k,v in self.data.items()}

    def __str__(self):
        def key(k):
            if isinstance(k, str):
                return "'%s'" % k
            return '%s' % k
        
        vals = '{%s}' % ', '.join([ '%s : %s' %(key(k), v) for k, v in self.vals().items()])
        return 'DictVal(%s)' %  (vals)


def var2val(var:Var|Val):
    if isinstance(var, (Val, Collection)):
        return var
    tp = var.getType()
    val = var.getVal()
    if isinstance(val, (Val, Collection)):
        return val
    return Val(val, tp)
