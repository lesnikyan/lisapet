
'''
Expressions of PatterMatch cases

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.iternodes import *
from nodes.keywords import *



# MATCH-CASE



class MCaseExpression(Expression):
    ''' '''


class MatchingPattern(Expression):
    ''' '''
    
    def __init__(self, src=None):
        super().__init__(None, src)

    # def setExp(self, exp:Exception):
    #     pass
    
    def match(self, val:Val):
        pass
    
    # def do(self, ctx:Context):
    #     pass
    
class MCValue(MatchingPattern):
    ''' 123 !- ... '''
    def __init__(self, expVal:Expression,  src=None):
        super().__init__(src)
        self.exp:Expression = expVal

    # def setExp(self, exp:Exception):
    #     self.exp = exp

    def do(self, ctx:Context):
        # print('MCVal.exp', self.exp)
        self.exp.do(ctx)
        
    def match(self, val:Val):
        # print('MCVal.exp', self.exp, self.exp.get(), ' >>', val)
        # if not scalar or string
        vtype = val.getType()
        if not isinstance(vtype, (TypeNum, TypeInt, TypeNull, TypeBool, TypeString)):
            # print('MCVal.match bad type', vtype, isinstance(vtype, TypeInt))
            return False
        if self.exp.get().getVal() == val.get():
            return True
        return False


class MC_Other(MatchingPattern):
    ''' _ !- ... '''

    def do(self, ctx:Context):
        # print('case-other.do')
        pass
        
    def match(self, val:Val):
        return True

class MCElem(MatchingPattern):
    ''' element of complex pattern '''



class MCSubVar(MCElem):
    ''' local subvar in pattern like: [a,b,c] '''

    def __init__(self, expVar:VarExpr,  src=None):
        super().__init__(src)
        self.exp:VarExpr = expVar
        self.var:Var = None

    def do(self, ctx:Context):
        # print('elem subvar.do1', self.exp)
        # self.exp.do(ctx)
        var = self.exp.get()
        ctx.addVar(var)
        self.var = var
        # print('elem subvar.do2', ctx.get('a'))
        
    def match(self, val:Val):
        self.var.set(val)
        self.var.setType(val.getType())
        return True

class MC_under(MCElem):
    ''' _ '''

    def do(self, ctx:Context):
        # print('elem `_`.do')
        pass
        
    def match(self, val:Val):
        return True

class MCContr(MatchingPattern):
    ''' pattern with sub-elements:
    collections, struct, etc'''
    
    def addSub(self, sub:MCElem):
        pass


class MCSerialVals(MCContr):
    ''' Pattern of serial set of values.
        basically: list, tuple
    '''
    
    def __init__(self,  src=None):
        super().__init__(src)
        self.elems:list[MCElem] = []

    def matchSerial(self, val:ListVal|TupleVal):
        vals = val.rawVals()
        vi = -1
        lenv = len(vals)
        for elem in self.elems:
            vi += 1
            if vi >= lenv:
                # pattern longer than value
                return False
            velem = vals[vi]
            if not elem.match(velem):
                return False
        if vi < (lenv - 1):
            # value longer than pattern
            return False
        return True


class MCList(MCSerialVals):
    ''' [], [123], [a,b], [_], [?], [*] '''
    
    def __init__(self,  src=None):
        super().__init__(src)

    def do(self, ctx:Context):
        for exp in self.elems:
            # print('MCList elem', exp)
            exp.do(ctx)
        
    def match(self, val:ListVal):
        if not isinstance(val.getType(), TypeList):
            return False
        return self.matchSerial(val)
    
    def addSub(self, sub:MCElem):
        self.elems.append(sub)


class MCTuple(MCSerialVals):
    ''' (), (_), (123), (a,b) '''
    
    def __init__(self,  src=None):
        super().__init__(src)

    def do(self, ctx:Context):
        for exp in self.elems:
            exp.do(ctx)
        
    def match(self, val:ListVal):
        if not isinstance(val.getType(), TypeTuple):
            return False
        
        return self.matchSerial(val)
    
    def addSub(self, sub:MCElem):
        self.elems.append(sub)


class MCKVPair(MCElem):
    ''' local subvar in pattern like: [a,b,c] '''

    def __init__(self, key, val,  src=None):
        super().__init__(src)
        # print('MCPairs init: ', self.__class__.__name__, key, val)
        self.key:MCElem = key
        self.val:MCElem = val

    def do(self, ctx:Context):
        # print('MCPairs.do', self.key)
        self.key.do(ctx)
        self.val.do(ctx)
        
    def match(self, vals:list):
        pass

class MCDPairKVal(MCKVPair):
    ''' 'abc':_ '''
        
    def match(self, vals:dict):
        k = var2val(self.key.exp.get()).getVal()
        kkl = list(vals.keys())
        # print('>>~>>', self.key.exp.get(), list(vals.keys()) , ' >> >>', k in kkl)
        n, m = Null(), Null()
        # print('m = n', n == m)
        # print('PairKVal - match:', k, ' in :', vals)
        if k not in vals:
            return 0, False
        # print('PairKVal - key passed', 'val:', vals[k])
        if not self.val.match(vals[k]):
            return 0, False
        vals.pop(k)
        return vals, True

class MCDPairVVal(MCKVPair):
    ''' 'abc':_ '''
        
    def match(self, vals:dict):
        # any key matches, finding val
        for k,v in vals.items():
            if self.val.match(v):
                kv = raw2val(k)
                self.key.match(kv) # if var-pattr of key
                vals.pop(k)
                return vals, True
        return 0, False

class MCDPairAny(MCKVPair):
    ''' var | _ '''

    def match(self, vals:dict):
        # any val matches, any first
        if len(vals) < 1:
            return 0, False
        for k, v in vals.items():
            kv = raw2val(k)
            if self.key.match(kv) and self.val.match(v):
                vals.pop(k)
                return vals, True
        return 0, False


class MCDict(MCContr):
    ''' {}, {_:v}, {a:b}, {'a':b} '''
    
    def __init__(self,  src=None):
        super().__init__(src)
        self.elems:list[MCKVPair] = []

    def addSub(self, sub:MCElem):
        self.elems.append(sub)

    def sortSubs(self):
        # sort by type
        # 1. const, 2. var, 3. _
        kc = [] # key is const-pattern
        vrr = [] # key is var-pattern
        _k = [] # key is _
        _v = [] # val is val-pattern
        # const-pattern has an advantage over `any` patterns (var | _)
        # key - over value
        for ee in self.elems:
            # print('MCDict.do', ee.__class__.__name__)
            if isinstance(ee.key, MCValue):
                kc.append(ee)
            elif isinstance(ee.key, MCSubVar):
                if isinstance(ee.val, MCValue):
                    _v.append(ee)
                else:
                    vrr.append(ee)
            elif isinstance(ee.key, MC_under):
                if isinstance(ee.val, MCValue):
                    _v.append(ee)
                else:
                    _k.append(ee)
            
        sels = kc + _v + vrr + _k
        self.elems = sels

    def do(self, ctx:Context):
        # print('MCDict.do', [em.__class__.__name__ for em in self.elems])
        for exp in self.elems:
            exp.do(ctx)

    def match(self, val:DictVal):
        if not isinstance(val.getType(), TypeDict):
            return False
        elemCount = len(self.elems)
        # vKeys = val.getKeys()
        # print('MCDict.match', [em.__class__.__name__ for em in self.elems])
        # vvals = val.vals()
        vvals = val.rawVals()
        # print('>>', vvals)
        if len(vvals) != elemCount:
            # print('Dc mt count failed')
            return False
        # if len(vvals) == 0:
        #     return True
        for pttr in self.elems:
            # pk, pv = pttr.key, pttr.val
            rem, ok = pttr.match(vvals)
            # print('Dpt.match', pttr.__class__.__name__, ok, rem)
            if ok:
                vvals = rem
        if len(vvals) == 0:
            return True


# -----------------

    
class MCStar(MCElem):
    ''' * '''

    def do(self, ctx:Context):
        # print('elem `*`.do')
        pass
        
    def match(self, val:Val|list[Val]):
        return True
    
class MCQMark(MCElem):
    ''' ? '''

    def do(self, ctx:Context):
        # print('elem `?`.do')
        pass
        
    def match(self, val:Val):
        return True

# --------------------

class CaseExpr(ControlBlock):
    ''' case in `match` block
    '''
    
    # TODO: do we need result from `match` blok?

    def __init__(self):
        # super().__init__()
        self.block = Block()
        self.expect:MatchingPattern = None
        # self.pattern:MatchingPattern = None

    def setExp(self, exp:Exception):
        # print('CaseExpr.setExp:', exp)
        self.expect = exp

    def doExp(self, ctx:Context):
        self.expect.do(ctx)

    def match(self, val:Val):
        return self.expect.match(val)

    def add(self, exp:Expression):
        self.block.add(exp)
    
    def do(self, ctx:Context):
        ''' body of sub-block '''
        self.block.do(ctx)
        self.lastVal = self.block.get()