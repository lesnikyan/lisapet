
from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

# from cases.tcases import *
from nodes.control import *
from nodes.match_patterns import *

from cases.tcases import *
from cases.oper import CaseBrackets, CaseBinOper, CaseVar
from cases.collection import *
from cases.structs import *
from cases.operwords import CaseRegexp


'''
Case detection.
! Note: pattern case is not a constructor-expression

# base: simple-val or data-struct

# data-struct: is list, dict, tuple, struct, (Maybe, Tree, etc)

# parse to elems.

# find quantifiers: `_ * ?`



'''


class MTCase(ExpCase):
    ''' case of match pattern '''
    
    def hasSubExpr(self):
        ''' For control cases in tree interprer '''
        return False

ValCases = [CaseVal(), CaseString()]

class MTVal(MTCase, CaseVal):
    ''' matching value
    12 !-
    true !-
    null !-
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        subEx = super().expr(elems)
        expr = MCValue(subEx, elems[0].text)
        return expr

class MTString(MTCase, CaseString):
    ''' matching value
    "abc" | 'aa' | `bb` !-
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        # print('>> MTString.expr', elemStr(elems))
        subEx = super().expr(elems)
        expr = MCValue(subEx, elems[0].text)
        return expr


class MTRegexp(MTCase, CaseRegexp):
    ''' regexp pattern
    '''
    def expr(self, elems:list[Elem])-> Expression:
        ''' Pattern: val '''
        # print('>> MTRegexp.expr', elemStr(elems))
        subEx, _ = super().split(elems)
        expr = MCRegexp(subEx, elems[0].text)
        return expr


class MTVar(MTCase,CaseVar):
    ''' '''    
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        vexpr = VarExpr(Var(elems[0].text, TypeAny()))
        ptt = MCSubVar(vexpr)
        return ptt


class MTObjMember(MTCase,CaseDotName):
    ''' MyEnum.name '''    
    
    
    def match(self, elems:list[Elem]) -> bool:
        ''' '''
        if len(elems) != 3:
            return False
        return super().match(elems)
        # ln = len(elems)
        # if ln < 3:
        #     return False
        # return isField(elems)
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''

        ename = elems[2].text
        objExpr = VarExpr(Var(elems[0].text, TypeAny()))
        member = VarExpr(Var(ename, TypeAny()))
        expr = OperDot(member)
        # print('MT.dot:setObj', objExpr)
        expr.setObj(objExpr)
        ptt = MCObjMember(expr)
        return ptt


_base_types = "int,float,bool,string,list,tuple,dict,struct,function".split(',')

class MTDuaColon(MTCase):
    ''' :: type  '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 2 and isLex(elems[0], Lt.oper, '::') and elems[1].type == Lt.word
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        tname = elems[1].text
        typeExpr = VarExpr(Var(tname, TypeAny()))
        return MCType(typeExpr, src=elems)


class MTTypedVal(MTCase):
    '''
        _ :: int
        abc :: int
        123 :: float
    '''
    
    # def __init__(self):
        # super().__init__()
        # self.typeOper = IsTypeExpr()
    
    def match(self, elems:list[Elem])-> bool:
        
        if len(elems) != 3:
            # no combo types
            return False
        if elems[0].type not in [Lt.word, Lt.num]:
            return False
        if not isLex(elems[1], Lt.oper, '::'):
            return False
        return elems[2].type == Lt.word
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        tname = elems[2].text
        typeExpr = VarExpr(Var(tname, TypeAny()))
        lelem = elems[:1]
        leftCase = findCase(lelem)
        if not leftCase:
            raise EvalErr("No correct left for MTTyped")
        left = leftCase.expr(lelem)
        return MCTypedElem(left, typeExpr, src=elems)


class MTMultiTyped(MTCase):
    '''
        n :: A | B
        _ :: int|float
        abc :: A|B
        n :: list|dict|tuple
        n :: (A|B|int)
    '''
    
    def findColons(self, elems):
        operInd = -1
        for i in range(2):
            if isLex(elems[i], Lt.oper, '::'):
                operInd = i
                break
        return operInd

    def match(self, elems:list[Elem])-> bool:
        # print('MTMultiTyped.match', elemStr(elems))
        if len(elems) < 2:
            return False
        # if isLex(elems[0], Lt.oper, '::')
        operInd = self.findColons(elems)
        if operInd < 0:
            return False
        
        # check left if has: xx :: ...
        if operInd > 0 and elems[0].type not in [Lt.word, Lt.num]:
            return False
        typeElems = elems[operInd+1:]
        # print('$MT-1', elemStr(typeElems))
        # has brackets (A | B)
        if isLex(elems[operInd+1], Lt.oper, '(') and isLex(elems[-1], Lt.oper, ')'):
            # print('$2', elemStr(typeElems))
            if isSolidExpr(elems[operInd+1:]):
                typeElems = typeElems[1:-1]
                # print('$3', elemStr(typeElems))
        # A | B | C
        elen = len(typeElems)
        for i in range(elen):
            n = typeElems[i]
            # print('6>>', n.text)
            if i % 2 == 0 and n.type != Lt.word:
                # print('MT1', i, elemStr(typeElems), n.text)
                return False
            elif i % 2 == 1 and not isLex(n, Lt.oper, '|'):
                # print('MT2', i, elemStr(typeElems), n.text)
                return False
        # print('Ok')
        return True

    def splitTypes(self, elems):
        # print('MT splitTypes', elemStr(elems))
        cases = [CaseBrackets(), CaseBinOper(), CaseVar()]
        subs = elems
        for cs in cases:
            if cs.match(subs):
                if cs.sub():
                    rexp, rsubs = cs.split(subs)
                    # print('$1>>', rexp, rsubs)
                    # subs = rsubs
                    if rsubs:
                        inExps = []
                        for rs in rsubs:
                            sexp = self.splitTypes(rs)
                            inExps.append(sexp)
                        # print('$2>>', rexp, inExps)
                        rexp = cs.setSub(rexp, inExps)
                    return rexp
                    # exp = rexp
                else:
                    return cs.expr(subs)
        raise EvalErr("Incorrect pattern of type, multitype MT-pattern.")

    # def split(self, elems:list[Elem])-> tuple[Expression, list[Elem]]:
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        # tname = elems[2].text
        # print()
        operInd = self.findColons(elems)
        typeElems = elems[operInd+1:]
        # print('$10>>', elemStr(typeElems))
        typeCase = self.splitTypes(typeElems)
        if not typeCase:
            raise EvalErr("Error during split of type-expr elems in MTTyped")
        # if no var `:: type`
        if operInd == 0:
            return MCType(typeCase, src=elems)
        # next for typed Var only
        lelem = elems[:1]
        leftCase = findCase(lelem)
        if not leftCase:
            raise EvalErr("No correct left for MTTyped")
        left = leftCase.expr(lelem)
        return MCTypedElem(left, typeCase, src=elems)


class MT_Other(MTCase, CaseVar_):
    ''' _ !-  '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '_')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MC_Other(src='_')


class SubElem(MTCase):
    ''' [{(_, ?, *)}] '''


class MTEStar(SubElem):
    ''' * '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.oper, '*')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MCStar(src='*')


class MTE_(SubElem):
    ''' _ '''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 1 and isLex(elems[0], Lt.word, '_')

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MC_under(src='_')


class MTEQMark(SubElem):
    ''' ? '''
    def match(self, elems:list[Elem])-> bool:
        # prels('MTEQMark len=', elems, show=1)
        return len(elems) == 1 and isLex(elems[0], Lt.oper, '?')

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return MCQMark(src='?')


class MTContr(MTCase):
    ''' pattern-container:
    collections, structs,etc'''

    def sub(self)->list[Elem]:
        return True

    def setSubs(self, base:MCContr, subs:list[MTCase]):
        for sub in subs:
            base.addSub(sub)


class MTComplex(MTCase):
    ''' combined case pattern
        ptt | ptt
        ptt :? ptt
    '''
    _priors = '( ) [ ] { } , | , : ,  `1`, :? '


class MTMultiCase(MTComplex):
    ''' one of pattern
        1 | 2 | 3 | [*]
    '''

    def match(self, elems:list[Elem]) -> bool:
        # priors = '( ) [ ] { } , | , : ,  `1`, :? '
        spl = OperSplitter(MTComplex._priors)
        opInd = spl.mainOper(elems)
        
        # print('MTMultiCase.match:', opInd, elems[opInd].text)
        return opInd > 0 and isLex(elems[opInd], Lt.oper, '|')

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ps = CaseSeq('|')
        subs = elems
        # print('MTMultiCase.expr:', self.__class__.__name__, '', subs)
        if ps.match(elems):
            _, subs = ps.split(elems)
        mcase = MCMultiCase(src=elems)
        for sub in subs:
            scase = findCase(sub)
            ptt = scase.expr(sub)
            mcase.add(ptt)
        return mcase


class MTPtGuard(MTComplex, SubCase):
    ''' expr :? expr '''
    
    def match(self, elems:list[Elem]) -> bool:
        # priors = '( ) [ ] { } , | , : ,  `1`, :? '
        spl = OperSplitter(MTComplex._priors)
        opInd = spl.mainOper(elems)
        
        # print('MTPtGuard.match:', opInd, elems[opInd].text)
        return opInd > 0 and isLex(elems[opInd], Lt.oper, ':?')

    def split(self, elems:list[Elem])-> tuple[Expression, list[Elem]]:
        # priors = '( ) [ ] { } , | , : ,  `1`, :? '
        spl = OperSplitter(MTComplex._priors)
        opInd = spl.mainOper(elems)
        left = elems[:opInd]
        patCase = findCase(left)
        pattr = patCase.expr(left)
        right = [Elem(Lt.word, 'if')] + elems[opInd+1:]
        expr = MCPtGuard()
        expr.pattern = pattr
        return expr, right
        
    def hasSubExpr(self):
        return True
    
    def setSub(self, base:MCPtGuard, subs:Expression)->Expression:
        # print('MTPtGuard.setSub', subs)
        base.setGuard(subs)
        return base


class CommaSeparatedSequence(MTContr):
    ''' {,,} [,,] (,,) '''

    def matchEdges(self, elems:list[Elem]):
        pass

    def match(self, elems:list[Elem]) -> bool:
        lem = len(elems)
        # prels('CommaSeparatedSequence', elems, show=1)
        if lem < 2:
            return False
        if not self.matchEdges(elems):
            return False
        if len(elems) == 2:
            return True
        priors = '( ) [ ] { } , | , : ,  `1` '
        spl = OperSplitter(priors)
        opInd = spl.mainOper(elems)
        # print('1>>>>>>>>>>>>', opInd,  elems[opInd].text)
        if opInd != 0:
            return False
        subElems = elems[1:-1]
        opInd = spl.mainOper(subElems)
        nosub = ';:'
        if isLex(elems[0], Lt.oper, '{'):
            # {a:b}
            nosub = ';'
        # print('2>>>>>>>>', opInd,  subElems[opInd].text)
        obrs = '([{'
        return opInd == -1 or (
            opInd == 0 and subElems[opInd].text in obrs ) or (
            opInd > 0 and subElems[opInd].text not in nosub)

    def split(self, elems:list[Elem]):
        sub = elems[1:-1]
        cs = CaseCommas()
        subs = []
        if sub:
            subs.append(sub)
        # print('SSq.split1:', self.__class__.__name__, '', [elemStr(s) for s in subs])
        if cs.match(sub):
            _, subs = cs.split(sub)
            # print('SSq.split2:','', [elemStr(s) for s in subs])
        subs = [sb for sb in subs if sb]
        # print(subs)
        # skipping empty sub [a, b, c, <empty part after last comma>]
        subPats = subPatterns(subs)
        res = []
        for sp in subPats:
            # print('sp:', type(sp))
            if isinstance(sp, (MCContr, MCStruct, MCType, MCTypedElem, MCRegexp, MCObjMember)):
                sp = MCSubCover(sp)
            res.append(sp)
        return res


class MTList(CommaSeparatedSequence):
    '''
    # Simple cases
    [], # empty
    [_], [_,_] # any val, no var assign
    [a], [a,b,c], [a,b,_] # var assign
    [_], [123,_], [_,123] # equal values
    # Complex cases.
    [?], [_,?], [4,?], [?,4] # maybe
    [*], [_,*], [123,*], [123,_,*], # others (any number of elems)
    # Nested
    [[]], [_,[]], [(),_], [{k:v}, {n:m}] # nested collections
    '''

    def matchEdges(self, elems:list[Elem]):
        return (isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'))

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subPtts = self.split(elems)
        # print('MTList.e subPtts:', subPtts)
        exp = MCList()
        self.setSubs(exp, subPtts)
        return exp


class MTTuple(CommaSeparatedSequence):
    ''' (), (1,), (1,2)
        (_), (1,_),
    '''

    def matchEdges(self, elems:list[Elem]):
        return (isLex(elems[0], Lt.oper, '(') and isLex(elems[-1], Lt.oper, ')'))

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subPtts = self.split(elems)
        # print('MTTuple.e subPtts:', subPtts)
        exp = MCTuple()
        self.setSubs(exp, subPtts)
        return exp


class MTColPair(MTContr, CaseColon):
    ''' pair with colon
        * : * 
    '''
    def match(self, elems:list[Elem]) -> bool:
        # print('MTColPair.match')
        return super(CaseColon,self).match(elems)

    def split(self, elems:list[Elem]):
        _, parts = super(CaseColon,self).split(elems)
        if len(parts) != 2:
            raise InterpretErr("Bad count of pair parts in MTColPair")
        # print('MTColPair.expr', parts)
        ekey = findCase(parts[0]).expr(parts[0])
        rval = findCase(parts[1]).expr(parts[1])
        return ekey, rval

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        '''
        order: key-val, val-val, key-type, val-type, any
        '''
        ekey, rval = self.split(elems)
        exp = None
        tkey = ekey
        if isinstance(tkey, MCTypedElem):
            tkey = tkey.left
        tval = rval
        if isinstance(tval, MCTypedElem):
            tval = tval.left
        if isinstance(tkey, MCValue):
            exp = MCDPairKVal(ekey, rval)
        elif isinstance(tkey, (MCSubVar, MC_under)):
            if isinstance(tval, MCValue):
                exp = MCDPairVVal(ekey, rval)
            else:
                exp = MCDPairAny(ekey, rval)
        elif isinstance(tkey, (MCTypedElem, MCType)):
            exp = MCDPairTyped(ekey, rval)
        else:
            # print('MTCol 1', ekey, rval)
            exp = MCDPairAny(ekey, rval)
        # print('MTColPair', elemStr(elems), exp, ekey, rval)
        return exp

class MTDict(CommaSeparatedSequence):
    '''
    {}, {'a':'b'}, {a:b}, {_:_}, {'a':_,*}, {'a':b, ?}
    '''
    
    def matchEdges(self, elems:list[Elem]):
        return (isLex(elems[0], Lt.oper, '{') and isLex(elems[-1], Lt.oper, '}'))
    
    def match(self, elems:list[Elem]) -> bool:
        if not super().match(elems):
            return False
        return True
        # TODO: more detail check of sub expressions

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subPtts = self.split(elems)
        exp = MCDict()
        # print('MTDict.e subPtts:', subPtts)
        self.setSubs(exp, subPtts)
        exp.sortSubs()
        return exp


class MTStruct(MTContr):
    ''' '''
    
    def __init__(self):
        self.struCase = CaseStructConstr()
    
    def match(self, elems:list[Elem]) -> bool:
        return (elems[0].type == Lt.word) and self.struCase.match(elems)

    def expr(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:

        constr, subs = self.struCase.split(elems)
        stype = elems[0].text
        # print('MTStruct', stype, subs)
        exp = None
        if stype == '_':
            exp = MCAnyStruct(src = elems)
        else:
            exp = MCStruct(stype, src = elems)
        for sub in subs:
            if isinstance(sub, NothingExpr) or len(sub) == 0:
                continue
            ptCase = findCase(sub)
            # print('MTStruct.sub:', elemStr(sub), ptCase)
            match ptCase:
                case MTColPair():
                    fvar, fpttr = ptCase.split(sub)
                    # print('Pair ...', fvar, fpttr)
                    if not isinstance(fvar, MCSubVar):
                        raise InterpretErr("MTStruct has incorrect field-name lexem.")
                    fname = fvar.exp.name
                    exp.add(fname, fpttr)
        return exp



class MTFail(MTCase):
    ''' case of incorrect pattern-syntax '''

    def expr(self, elems:list[Elem]):
        raise InterpretErr("Incorrect pattern-matching sequence")


pMListInnerCases:list[MTCase] = [
    MTMultiCase(), MTTypedVal(), MTDuaColon(), MTMultiTyped(),
    MTVal(), MTE_(), MTVar(), MTString(), MTRegexp(), MTObjMember(),
    MTEStar(),  MTEQMark(), MTColPair(),
    MTList(), MTTuple(), MTDict(), MTStruct(), 
]


def findCase(elems:list[Elem])->MTCase:
    # print('finCase', elems)
    # prels('findCase1:', elems, show=1)
    for cs in pMListInnerCases:
        if cs.match(elems):
            # print('finCase >>> ', cs.__class__.__name__)
            return cs
    return MTFail()

def subPatterns(subs:list[list[Elem]])->list[MTCase]:
    if len(subs) == 0:
        return []
    res = []
    # print('subPatterns#00:', subs)
    for sub in subs:
        ptCase = findCase(sub)
        # print('subPatterns#1:', elemStr(sub), ptCase.__class__)
        # if isinstance(ptCase, MTFail):
        #     print(' !! > MP-sub. fail', elemStr(sub))
        ptt = ptCase.expr(sub)
        res.append(ptt)
    
    return res



