'''
ExpCases here for exec tree
'''

import os
import re

from lang import *
from vars import *
from vals import elem2val, isLex

from cases.utils import *

from nodes.tnodes import *

from nodes.oper_dot import OperDot
from nodes.oper_nodes import *
from nodes.datanodes import *
from nodes.control import *
from nodes.func_expr import *


EXT_ASSIGN_OPERS = '+= -= *= /= %='.split(' ')


# _opers = ''.split('= += -= *= /= %=')
def afterLeft(elems:list[Elem])->int:
    ''' find index of elem after var, vars and possible brackets of collections elem
    cases:
        var ...
        a, b, c ...
        arr[expr] ... 
        arr[axpr + expr] ...
        obj.field[key].field ...
        obj.meth(arg).field[key].field ...
    '''
    res = -1
    inBr = 0
    elran =  range(len(elems))
    for i in elran:
        ee = elems[i]
        # dprint(ee.text)
        if inBr:
            # if ee.text == ']':
            # dprint('in BR. continue', ee.text, ee.text in ')]')
            if ee.text in ')]':
                # close brackets
                inBr -= 1
                continue
        # dprint('inbr ', inBr)
        # if ee.type == Lt.oper and  ee.text == '[':
        if ee.type == Lt.oper and  ee.text in '([':
            # enter into brackets
            inBr += 1
            continue
        if inBr:
            continue
        # dprint('@@ after', i, elems[i].text)
        if i > 0 and ee.type != Lt.word and (ee.type == Lt.oper and ee.text not in '.,:'):
            # dprint('break:<(', ee.text,')> >> ',  elemStr(elems[:i+1]))
            res = i
            break
    return res


def _bracketsPart(elems:list[Elem])->int:
    ''' find index of elem after var/func Name and possible brackets
    cases:
        var ...
        foo(arg, arg, arg) ...
        arr[expr] ... 
    '''
    if len(elems) < 2:
        return -1 # means not brackets
    res = 0
    inBr = ''
    obr = '([{'
    cbr = ')]}'
    if elems[0].text not in obr:
        return -1
    elran = range(len(elems))
    for i in elran:
        ee = elems[i]
        # print(' >>> ', ee.text)
        # if inBr:
        if ee.text == '':
            continue
        if ee.text in cbr :
            # print('#close', ee.text)
            if obr.index(inBr[-1]) != cbr.index(ee.text):
                # print('# ee:', ee.text, 'inbr:', inBr, ' ,, cbr:', cbr)
                raise ParseErr('Incorrect brackets combinations %s on position ' % ''.join([n.text for n in elems]))
            # close brackets
            inBr = inBr[:-1]
            if len(inBr) == 0:
                # last bracket was closed
                if i + 1 < len(elems):
                    return i + 1
                return -1
            continue
        if ee.type == Lt.oper and  ee.text in obr:
            # enter into brackets
            inBr += ee.text
            # dprint('#open:', inBr)
            continue
        if inBr:
            continue
        if i > 0:
            res = i
            break
    return res


def firstBrackets(elems:list[Elem]):
    ''' For 1-lvl brackets only '''
    elen = len(elems)
    a, b = -1, -1
    for i in range(elen):
        ee = elems[i]
        if ee.type != Lt.oper:
            continue
        if ee.text == '(':
            a = i
            continue
        if ee.text == ')':
            b = i
            break
    return a, b


def endsWithBrackets(elems:list[Elem], br='()'):
    ''' any expr which ends with something(or nothing) in brackets 
        expr(); expr[expr]; expt{expr}
        (): foo(arg), obj.foo(obj.val), arr[expr].foo(arr[expr])
        []: obj.arr[expr], arr[obj.arr[expr]], arr[obj.sub.foo(arg)], dictVal[keyExpr][arrIndex][arrIndex]
        {}: SType{expr, expr}; foo(SType{expr, expr}); foo(struct{field:val, field:val}); foo({key:val, key:val})
    '''
    lem = len(elems)
    if lem < 2:
        return False
    
    bopen, bclose = br
    if not isLex(elems[-1], Lt.oper, bclose):
        return False

    opInd = findLastBrackets(elems)
    return opInd > 0


_opnBrs = list('([{')
_cloBrs = list(')]}')

def findLastBrackets(elems:list[Elem]):
    ''' return index of opening of last brackets in explession '''
    lem = len(elems)
    inBr = 0
    # obrs = '( [ {'.split(' ')
    # cbrs = ') ] }'.split(' ')
    if not isLex(elems[-1], Lt.oper, _cloBrs):
        # incorrect elems data
        return -1

    for i in range(lem-1, -1, -1):
        ee = elems[i]
        if ee.type != Lt.oper:
            continue
        if ee.text in _cloBrs:
            # step in brackets
            inBr += 1
            continue
        if ee.text in _opnBrs: 
            # step out from brackets
            inBr -= 1
            if inBr == 0:
                return i
            continue
    return -2 # just for debug needs



class ExpCase:
    ''' '''
    def match(self, elems:list[Elem])-> bool:
        pass
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        pass
    
    def sub(self)->list[Elem]:
        return None
    
    def isLim(self):
        return False


class SolidCase:
    ''' solid expressions '''


class CaseComment(ExpCase):
    ''' possibly will be used for meta-coding'''
    def match(self, elems:list[Elem])-> bool:
        if len(elems) == 0:
            return False
        # s = ''.join([n.text for n in elems])
        if elems[0].type == Lt.comm:
            # dprint('CaseComment.match', s)
            return True
        return False

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        CommentExpr(''.join([n.text for n in elems]).lstrip())


class CaseEmpty(ExpCase):
    ''' possibly will be used for meta-coding'''
    def match(self, elems:list[Elem])-> bool:
        return len(elems) == 0

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        return NothingExpr()


class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        # prels('--DEbug', elems)
        return len(elems) > 1 and elems[1].text == 'debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))
 
 
class UnclosedExpr:
    ''' '''
    def __init__(self, elems:list):
        # super().__init__('')
        self.elems:list = elems
        
    def init(self, cline:CLine):
        self.src = cline.src
        self.indent = cline.indent

    def add(self, part:list, src:TLine):
        self.elems.extend(part)
        self.src.add(src)


class CaseUnclosedBrackets(ExpCase):
    
    def match(self, elems:list[Elem])-> bool:
        # prels('--', elems)
        inBr = 0
        maxLvl = 0
        for el in elems:
            if el.type != Lt.oper:
                continue
            if el.text in _opnBrs:
                inBr += 1
                if maxLvl < inBr:
                    maxLvl = inBr
                continue
            if el.text in _cloBrs:
                inBr -= 1
            
        return maxLvl > 0 and inBr > 0
                
        
    def expr(self, elems:list[Elem])-> Expression:
        ''' return elems covered by operation case '''
        return UnclosedExpr(elems)


class CaseVal(ExpCase, SolidCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        pass
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        # prels('CaseVal.expr:', elems, show=1)
        res = ValExpr(elem2val(elems[0]))
        # print('## CaseVal', res.get().getVal(), res.get().vtype.__class__.__name__)
        return res

_numConsts = ['true', 'false', 'null']

class CaseNumVal(CaseVal, SolidCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) != 1:
            return False
        # prels('CaseVal.match:', elems, show=1)
        if elems[0].type in [Lt.num]:
            return True
        return  isLex(elems[0], Lt.word, _numConsts)
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        # prels('CaseVal.expr:', elems, show=1)
        res = ValExpr(elem2val(elems[0]))
        # print('## CaseNumVal', res.get().getVal(), res.get().vtype.__class__.__name__)
        return res


class CaseVar(ExpCase, SolidCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        # print('CaseVar', elems)
        if len(elems) > 1:
            return False
        if elems[0].type == Lt.word:
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        expr = VarExpr(Var(elems[0].text, TypeAny())) # Any for non-typed vars
        return expr

class CaseVar_(ExpCase, SolidCase):
    ''' _ var
        null-assign var
        value won't assigned
    '''
    def match(self, elems:list[Elem]) -> bool:
        return len(elems) > 1 and isLex(elems[0], Lt.word, '_')
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        expr = VarExpr_(Var_())
        return expr


class SubCase(ExpCase):
    ''' Basic for any complex cases like operator, function, method call '''

    def sub(self):
        return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        pass
    
    def setSub(self, base:Expression, subs:list[Expression])->Expression:
        pass


class BlockCase(ExpCase):
    ''' control sub and inner sub 
        function, for-loop, if-statement, match-case statement
    '''

_rArrCh = '->'
_bslCh = '\\'


class CaseSeq(SubCase):
    ''' sequence of expressions in one line '''
    
    def __init__(self, delim=' '):
        self.delim = delim
        self.brs = {'(':')', '[':']', '{':'}'}
        self.opens = self.brs.keys()
        self.closs = self.brs.values()

    def match(self, elems:list[Elem], ind=None) -> bool:
        # prels('CaseSeq.match %s'% self.delim, elems, show=1)
        delimord = [':',',',';']
        dmInds = {delimord[i] : i for i in range(len(delimord))}
        baseDelInd = len(delimord)
        if self.delim in delimord:
            baseDelInd = delimord.index(self.delim)
        obr = 0 # bracket counter
        lamArgs = False # right of `\` and left of `->`
        
        # check without control of nesting, just count open and close brackets
        found = False
        for ee in elems:
            if ee.type != Lt.oper:
                continue
            if ee.text in self.opens:
                obr += 1
                continue
            if ee.text in self.closs:
                obr -= 1
                continue
            if obr > 0:
                # in brackets, ignore internal elems
                continue

            # lambda-args case
            if lamArgs:
                if ee.text == _rArrCh:
                    lamArgs = False
                continue
            if ee.text == _bslCh:
                lamArgs = True

            if ee.text in dmInds and dmInds[ee.text] > baseDelInd:
                # break if has delim in later pos
                return False
            if ee.text == self.delim:
                found = True
        return found

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        res = []
        sub = []
        obr = 0
        start = 0
        lamArgs = False
        elen = len(elems)
        for i in range(elen):
            ee = elems[i]
            if ee.type != Lt.oper:
                continue
            if ee.text in self.opens:
                obr += 1
                continue
            if ee.text in self.closs:
                obr -= 1
                continue
            if obr > 0:
                # in brackets, ignore internal elems
                # sub.append(ee)
                continue
            
            # lambda args changes behaviour of separator
            if lamArgs:
                if ee.text == _rArrCh:
                    lamArgs = False
                continue
            if ee.text == _bslCh:
                lamArgs = True
                
            if ee.text == self.delim:
                sub = elems[start: i]
                # prels('# start= %d, i= %d sub:' % (start, i), sub)
                start = i + 1
                res.append(sub)
                continue
        # print('Seq.split, start =', start, 'len-elems =', len(elems))
        if start < len(elems):
            res.append(elems[start:])
        # if isLex(res[0][0], Lt.oper, self.delim):
        #     res = [[]] + res
        if isLex(elems[-1], Lt.oper, self.delim):
            res.append([])
        return SequenceExpr(self.delim), res

    def setSub(self, base:SequenceExpr, subs:Expression|list[Expression])->Expression:
        # print('CaseSeq(%s) setSub: ' % self.delim, base, subs)
        for sub in subs:
            base.add(sub)
        return base


class CaseSemic(CaseSeq, SubCase):
    ''' Semicolons out of controls cases. The same as one-line block
        a=5; b = 7 + foo(); c = a * b
        uses if not control structure like: if, for, etc
    '''

    def __init__(self):
        super().__init__(';')


    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        base, subs = super().split(elems)
        src = elemStr(elems)
        base = LineBlockExpr(src)
        return base, subs
        

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # print('CaseSemic setSub: ', base, subs)
        for s in subs:
            if isinstance(s, NothingExpr):
                continue
            base.add(s)


class CaseCommas(CaseSeq):
    ''' a, b, foo(), 1+5  '''
    def __init__(self):
        super().__init__(',')


class CaseColon(CaseSeq):
    ''' key: val  '''
    def __init__(self):
        super().__init__(':')


class CaseDot(CaseSeq):
    ''' key.val  '''
    def __init__(self):
        super().__init__('.')


class RawCase:
    ''' case we need do some post-operation '''


class ArrOper(RawCase):
    def __init__(self, left=None, right=None):
        self.left:Expression = left
        self.right:Expression = right

class MatchPtrCase(RawCase):
    def __init__(self, left=None, right=None):
        self.left:Expression = left
        self.right:Expression = right


class CaseDotName(SubCase, SolidCase):
    ''' solidExpr.name:
        obj.name
        "str".split
        [1,2,3].map
        foo().field
        nn[key].field
    
    '''

    def match(self, elems:list[Elem], ind=-1) -> bool:
        ''' '''
        ln = len(elems)
        if ln < 3:
            return False
        return isField(elems)

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        fname = elems[-1].text
        member = VarExpr(Var(fname, TypeAny()))
        expr = OperDot(member)
        return expr, [elems[:-2]]
    
    def setSub(self, base:OperDot, subs:Expression|list[Expression])->Expression: 
        ''' '''
        objExpr = subs[0]
        # print('O.dot:setSub', objExpr)
        base.setObj(objExpr)
        return base
