
'''
Expressions of PatterMatch cases

pattern !- executable block

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.iternodes import *
from nodes.keywords import *



class MCaseExpression(Expression):
    ''' '''

# ------------------- Pattern cases -------------------- #


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

    def do(self, ctx:Context):
        self.exp.do(ctx)
        
    def match(self, val:Val):
        # if not scalar or string
        # print('MCValue match', 'expr:', self.exp)
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
        pass
        
    def match(self, val:Val):
        return True


class MCElem(MatchingPattern):
    ''' element of complex pattern '''


# ------------------------ Sub-elements of sequence ---------------------- #


class MCSub(MCElem):
    ''' base of list|tuple subs '''

    def match(self, val:Val):
        # print('!!! MMCSub. MATCH @@@@')
        pass

    def matchInd(self, index:int, vals:list[Val]):
        '''match elem in list by index'''
        # print('MSub.matchInd', vals[index])
        val = vals[index]
        return self.match(val)


class MCSubVal(MCSub):
# class MCSubVal(MCValue, MCSub):
    ''' [1, 'a'] '''
    
    def __init__(self, mcVal:MCValue):
        super().__init__(mcVal.src)
        self.mcVal = mcVal
    
    def match(self, val:Val):
        # print('MCSubVal match')
        return self.mcVal.match(val)


class MCSubVar(MCSub):
    ''' local subvar in pattern like: [a,b,c] '''

    def __init__(self, expVar:VarExpr,  src=None):
        super().__init__(src)
        self.exp:VarExpr = expVar
        self.var:Var = None
        self.ctx = None

    def do(self, ctx:Context):
        # just store new context instance
        # preventing store previous value of var for run of the same pattern
        self.ctx = ctx
        var = self.exp.get()
        self.var = var

    def match(self, val:Val):
        # add new var into sub-context
        self.ctx.addVar(self.var)
        self.var.set(val)
        self.var.setType(val.getType())
        return True


class MC_under(MCSub):
    ''' [{( _ )}] '''

    def do(self, ctx:Context):
        # do nothing because `_` pattern doesn't assign or read value
        pass

    def match(self, _):
        return True


class MCStar(MCSub):
    ''' * '''

    def do(self, _):
        # print('elem `*`.do')
        pass

    def match(self, val:Val|list[Val]):
        return True

    
class MCQMark(MCSub):
    ''' ? in list, tuple '''

    def do(self, ctx:Context):
        # print('elem `?`.do')
        pass
        
    def match(self, val:Val):
        '''
        [1, ?, 2]
        [1,2]
        [1, 0, 2]
        --
        [1, ?, ?, 5, 2]
        [1, 5, 2]
        [1,3,5,2]
        [1,5,5,2]
        [1, 5,3, 5,2]
        
        '''
        return True


# -------------------- Ordered sequences ---------------- #


class MCContr(MatchingPattern):
    ''' Container-pattern - complex pattern with sub-elements:
    collections, struct, etc'''

    def addSub(self, sub:MCElem):
        # Add sub-element of collection-pattern
        pass


def mcIsMaybe(elem:MCElem):
    return isinstance(elem, (MCQMark))


def mcIsStar(elem:MCElem):
    return isinstance(elem, (MCStar))


def mcIsQm(elem:MCElem):
    return isinstance(elem, (MCQMark))


class MCSerialVals(MCContr):
    ''' Pattern of serial set of values.
        basically: list, tuple
    '''

    def __init__(self,  src=None):
        super().__init__(src)
        self.elems:list[MCElem] = []
        self.hasMaybe = False
    
    def addSub(self, sub:MCElem):
        if isinstance(sub, MCValue):
            sub = MCSubVal(sub)
        # print(self.__class__.__name__, hash(self), '.add:', sub.__class__.__name__)
        if mcIsMaybe(sub) or mcIsStar(sub):
            self.hasMaybe = True
        self.elems.append(sub)

    def matchSerial(self, val:ListVal|TupleVal):
        vals = val.rawVals()
        # mi = -1 # pattern indes
        lenv = len(vals)
        # print('\n', self.__class__.__name__, 'match', val.vals(), ', subs:', len(self.elems))
        # print('#0', [n.__class__.__name__ for n in self.elems])
        if not self.hasMaybe:
            if lenv != len(self.elems):
                # print('SqMatch: bad count')
                return False
        
        def backMatch(i, count, melem:MCElem):
            ''' finding match from vals[i] '''
            # print('backM:', i, count, melem, [v.getVal() for v in vals])
            for vvi in range(i, i + count, 1):
                # print('backm loop:', vvi, ':', vals[vvi].getVal())
                if melem.match(vals[vvi]):
                    # print('back matched:', vvi)
                    return vvi
            return -1 # not matchd
        
        def backVars(i, mels:list[MCElem]):
            ''' mels should be instance of MC_under|MCSubVar '''
            vvi = i
            # for vvi in range(i, i + len(mels)):
            # print('backVars#1', vvi)
            for mel in mels:
                mel.match(vals[vvi])
                vvi += 1
        
        def isSubVal(elem:MCElem):
            return isinstance(elem, MCSubVal)
        
        mInd = -1
        mLast = len(self.elems) - 1
        vi = -1 # value index
        indiff = 1
        qmCount = 0
        instar = False
        varPref = [] # var|_ prefix after `?`
        # cases: 1) SubVal, 2) Var|_under, 3) ?, 4) *
        for elem in self.elems:
            # print('list match loop', elem)
            mInd += 1
            # if qmCount > 0:
            #     qmCount -= 1
            indiff = 1
            if mcIsMaybe(elem):
                indiff = 0
                if mcIsQm(elem):
                    qmCount +=1
                    
                    # if mInd == mLast:
                        
                # else:
                    # qmCount = 0
                # we dont't need call match of ?, * cases
                continue
            if mcIsStar(elem):
                instar = True
                qmCount +=1
                if lenv > 0:
                    qmCount = lenv - vi
                # print('mp-star case', qmCount)
                continue
                
            # after qm-queue
            if qmCount:
                # if vars or _under after ?, ?
                if isinstance(elem, (MC_under, MCSubVar)):
                    varPref.append(elem)
                    continue
                
                if isSubVal(elem):
                    # vi += 1
                    # oldVi = vi
                    # [?, 2]
                    # [2]
                    # [1, 2]
                    # [1, ?, _, a, 2]
                    # [1, 4, 5, 2]
                    # [1, 3, 4, 5, 2]
                    varpLen = len(varPref)
                    findCount = qmCount + 1
                    findIndex = vi + 1 + varpLen
                    if findIndex >= lenv:
                        # already out of vals
                        return False
                    # prevent index out of range
                    if findCount + findIndex >= lenv:
                        findCount = lenv - findIndex
                    # print('inSub', findIndex, findCount, elem)
                    bi = backMatch(findIndex, findCount, elem)
                    if bi > vi:
                        vi = bi
                        qmCount = 0
                        instar = False
                        # assign prev vars
                        if varpLen:
                            # print('varPref:', varPref)
                            backVars(vi - varpLen, varPref)
                            varPref = []
                        continue
                    # fail if no one has been matched
                    return False
            
            # ordinar cases:
            vi += indiff
            if vi >= lenv:
                # pattern longer than value
                return False
            
            # print('listMatch #ordinar:', vi, elem.__class__)
            if not elem.matchInd(vi, vals):
                # print('SqMatch: not match')
                # if in question-marks queue
                # if qmCount > 0:
                #     # qmCount -= 1
                #     continue
                return False
                
            # print('match is mayb:', mcIsMaybe(elem), 'valInd:', vi)

        varpLen = len(varPref)
        # print('\nLMatch: after loop: vi=%d, len-vals=%d' % (vi, lenv), 'qm=', qmCount)
        # print([n.get() for n in vals])
        if vi < (lenv - 1):
            # print('#1', [n.__class__.__name__ for n in self.elems])
            if qmCount:
                # print('#2 ?', qmCount, ' >', lenv -1 - vi, ', vi=', vi)
                if qmCount >= lenv -1 - vi:
                    # print('#3 lenv=%d, vi=%d,  vi - varpLen=%d (L -1 - vi)= %d' % (lenv, vi,  varpLen, (lenv -1 - vi)), varPref)
                    if varpLen <= (lenv -1 - vi):
                        # print('end backVars::', vi - varpLen, varPref)
                        backVars(lenv - varpLen, varPref)
                    
                    # print('#3')
                    return True
            # print('#2')
            # value longer than pattern
            # print('SqMatch: shorter pattr')
            return False
        # print('list match end-True')
        return varpLen == 0


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
    
    # def addSub(self, sub:MCElem):
    #     self.elems.append(sub)


# ----------------- Dict and sub-dict patterns -------------------- #


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


class MCDPairStar(MCKVPair):
    ''' star in dict {.., * } '''

    def __init__(self, src=None):
        super().__init__(None, src)

    def do(self, ctx:Context):
        # print('elem `*`.do')
        pass

    def match(self, vals:dict):
        # vals.pop(k)
        return [], True


class MCDPairQMark(MCKVPair):
    ''' question mark in dict {.., ? } 
        can match 1 sub-element of dict, or nothing == unnecessary element
        {?} means empty dict or 1 pair inside
    '''

    def __init__(self, src=None):
        super().__init__(None, src)

    def do(self, ctx:Context):
        # print('elem `*`.do')
        pass

    def match(self, vals:dict):
        # if not len(vals):
        #     return vals, False
        for k in vals.keys():
            vals.pop(k)
            break
        return vals, True
        # return vals, False


class MCDict(MCContr):
    ''' dict-pattern
        {}, {_:v}, {a:b}, {'a':b, _:''} '''
    
    def __init__(self,  src=None):
        super().__init__(src)
        self.elems:list[MCKVPair] = []
        self.hasStar = False
        self.qmarkCount = 0

    def addSub(self, sub:MCElem):
        self.elems.append(sub)

    def sortSubs(self):
        # sort by type
        # 1. const, 2. var, 3. _
        kc = [] # key is const-pattern
        vrr = [] # key is var-pattern
        _k = [] # key is _
        _v = [] # val is const-pattern
        stars = []
        qm = []
        # const-pattern before `any` patterns (var | _)
        # key - before value
        for ee in self.elems:
            # print('MCDict.do', ee.__class__.__name__)
            if isinstance(ee, MCStar):
                stars.append(MCDPairStar())
                self.hasStar = True
                continue
            if isinstance(ee, MCQMark):
                qm.append(MCDPairQMark())
                self.qmarkCount += 1
                continue
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
            
        sels = kc + _v + vrr + _k + qm + stars
        self.elems = sels

    def do(self, ctx:Context):
        # print('MCDict.do', [em.__class__.__name__ for em in self.elems])
        for exp in self.elems:
            exp.do(ctx)

    def match(self, val:DictVal):
        if not isinstance(val.getType(), TypeDict):
            return False
        elemCount = len(self.elems)
        # print('MCDict.match', [em.__class__.__name__ for em in self.elems])
        vvals = val.rawVals()
        # print('>>', vvals)
        if not self.hasStar and not self.qmarkCount:
            if len(vvals) != elemCount:
                # print('Dc mt count failed')
                return False
        for pttr in self.elems:
            # pk, pv = pttr.key, pttr.val
            rem, ok = pttr.match(vvals)
            # print('Dpt.match', pttr.__class__.__name__, ok, rem)
            if not ok:
                return False
            vvals = rem
        # in correct match all pairs was matched and removed from vvals
        return not vvals


# -------------------- Whole Case ------------------- #


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