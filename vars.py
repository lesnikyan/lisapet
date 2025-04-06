

from lang import *
from base import *
from typex import *


# class Var(Base):
#     def __init__(self, val:Base, name=None, vtype:VType=None):
#         self.val:Base = val
#         self.name = name # if name is none - here Val, not Var
#         self.vtype:VType = vtype
    
#     def set(self, val):
#         self.val = val
    
#     def get(self):
#         return self.val
    
#     def setType(self, t:VType):
#         self.vtype = t
    
#     def getType(self):
#         return self.vtype
    
#     def __str__(self):
#         n = self.name
#         if not n:
#             n = '#noname'
#         tt = '#undefined'
#         if self.vtype is not None:
#             tt = self.vtype.name
#         return '%s(%s, %s: %s)' % (self.__class__.__name__, n, self.val, tt)


class VarType(Var):
    def __init__(self, val:VType, vtype = VType):
        super().__init__(val, 'type_%s' % vtype.name, vtype)


class Var_(Var):
    ''' expr: _ '''
    name = '_'
    def __init__(self):
        self.vtype:VType = TypeNull
        self.val = None


class VarUndefined(Var):
    def __init__(self, name):
        super().__init__(None, name, Undefined)


class VarNull(Var):
    ''' None|null'''

    def __init__(self, name=None):
        super().__init__(None, name, TypeNull)

    def setType(self, t:VType):
        pass


def value(val, vtype:VType)->Var:
    return Var(val, None, vtype)

# type: Comparable, Container, Numeric 

class CompVar(Var):
    def compare(self, other:'CompVar')-> int:
        a, b = self.get(), other.get()
        if a == b:
            return 0
        return a - b


class VarRatio(CompVar):
    def __init__(self, a:int, b:int, name=None):
        super().__init__(0, name, TypeRatio)
        self.numer:int = a # numerator
        self.denom:int = b # denominator

    def float(self):
        return Var(self.name, self.numer / self.denom, TypeFloat)


class FuncRes(Var):
    ''' '''
    def __init__(self, val):
        super().__init__(val, None)


# Collections

class Container(Var):
    ''' Contaiter Var list, dict, etc '''
    
    def setVal(self, key:Var, val:Var):
        pass

    def getVal(self, key:Var):
        pass


class Collection(Container):
    
    def len(self)->int:
        return 0

    def vals(self):
        pass


class ListVar(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, name=None, **kw):
        super().__init__(None, name, TypeList)
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Var] = ees

    def len(self)->int:
        return len(self.elems)
    
    def addVal(self, val:Var):
        # not sure, we need whole Var or just internal value?
        self.elems.append(val)
    
    def setVal(self, key:Var, val:Var):
        i = key.get()
        # print('ListVar.setVal', i, val, 'Len=', len(self.elems), i < len(self.elems), self.elems)
        if i >= len(self.elems):
            raise EvalErr('List out of range by index %d ' % i)
        self.elems[i] = val

    def getVal(self, key:Var|int):
        print('ListVar.getVal1, key:', key)
        # print('ListVar.getVal1, elems:', self.elems)
        i = key
        if isinstance(key, Var):
            i = key.get()
        print('@ i=', i)
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('List out of range by index %d ' % i)

    def getSlice(self, beg, end):
        if beg < 0 or end > len(self.elems):
            raise EvalErr('indexes of List slice are out of range [%d : %d] with len = %d' % (beg, end, len(self.elems)))
        rdata = self.elems[beg: end]
        return ListVar(elems=rdata)

    def get(self):
        return  [n.get() for n in self.elems] # debug
        # return self.elems

    def vals(self):
        return [str(n.get()) for n in self.elems[:10]]

    def __str__(self):
        nm = self.name
        if not nm:
            nm = '#list-noname'
        def strv(var):
            # print('@>>', var, var.getType())
            if isinstance(var.getType(), TypeContainer):
                return str(var)
            return str(var.get())
        vals = [strv(n) for n in self.elems[:10]]
        return 'ListVar(%s, [%s])' % (nm, ', '.join(vals))


class TupleVar(Collection):
    ''' '''
    def __init__(self, name=None, **kw):
        super().__init__(None, name, TypeList)
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Var] = ees

    def len(self)->int:
        return len(self.elems)

    def addVal(self, val:Var):
        self.elems.append(val)

    def getVal(self, key:Var|int):
        i = key
        if isinstance(key, Var):
            i = key.get()
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('Tuple out of range by index %d ' % i)


class DictVar(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, name=None):
        super().__init__(None, name, TypeDict)
        self.data:dict[Var,Var] = {}

    def len(self)->int:
        return len(self.data)
        
    def inKey(self, key:Var)->str:
        return '%s__%s' % (key.get(), key.getType().__class__.__name__)

    def setVal(self, key:Var, val:Var):
        # k = self.inKey(key)
        self.data[key.get()] = val

    def getKeys(self):
        # res = [ListVar(k) for k in self.data]
        res = ListVar()
        for k in self.data:
            res.addVal(k)
        return res

    def getVal(self, key:Var):
        # k = self.inKey(key)
        k = key.get()
        if k in self.data:
            return self.data[k]
        raise EvalErr('List out of range by key %s ' % k)

    def vals(self):
        return {k: v.get() for k,v in self.data.items()}

