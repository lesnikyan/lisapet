'''
ExpCases here for exec tree
'''

import os

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.utils import *

from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.datanodes import *
from nodes.control import *
from nodes.func_expr import *


EXT_ASSIGN_OPERS = '+= -= *= /= %='.split(' ')


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
    opers = ''.split('= += -= *= /= %=')
    
    for i in range(len(elems)):
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


def brAfterExpr(elems:list[Elem])->int:
    ''' find index of elem after var/func Name and possible brackets
    cases:
        foo()
        foo(arg, arg, arg)
        arr[expr]
        ()()
        nn[]()
        foo()()
        {expr}({args})
        {expr} = [name]brackets 
        {solidExpression}([args])
    '''
    res = 0
    inBr = ''
    obr = '([{'
    cbr = ')]}'
    for i in range(len(elems)):
        ee = elems[i]
        # if inBr:
        if ee.text in cbr :
            # dprint('#close', ee.text)
            if obr.index(inBr[-1]) != cbr.index(ee.text):
                # dprint('# ee:', ee.text, 'inbr:', inBr)
                raise ParseErr('Incorrect brackets combinations %s on position %d %s ' % ''.join([n.text for n in elems]))
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


def bracketsPart(elems:list[Elem])->int:
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
    for i in range(len(elems)):
        ee = elems[i]
        dprint(' >>> ', ee.text)
        # if inBr:
        if ee.text in cbr :
            dprint('#close', ee.text)
            if obr.index(inBr[-1]) != cbr.index(ee.text):
                # dprint('# ee:', ee.text, 'inbr:', inBr)
                raise ParseErr('Incorrect brackets combinations %s on position %d %s ' % ''.join([n.text for n in elems]))
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
            dprint('#open:', inBr)
            continue
        if inBr:
            continue
        if i > 0:
            res = i
            break
    return res



class ExpCase:
    ''' '''
    def match(self, elems:list[Elem])-> bool:
        pass
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        pass
    
    def sub(self)->list[Elem]:
        return None


class CaseComment(ExpCase):
    ''' possibly will be used for meta-coding'''
    def match(self, elems:list[Elem])-> bool:
        if len(elems) == 0:
            return False
        s = ''.join([n.text for n in elems])
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


class CaseVal(ExpCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) != 1:
            return False
        # prels('CaseVal.match:', elems, show=1)
        if elems[0].type in [Lt.num]:
            return True
        if isLex(elems[0], Lt.word, 'null'):
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = ValExpr(elem2val(elems[0]))
        # print('## CaseVal', res.get().vtype)
        return res


class CaseString(CaseVal):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        # print('StrCase:', elems)
        if len(elems) != 1:
            return False
        if elems[0].type in [Lt.text, Lt.mttext]:
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = StringExpr(elem2val(elems[0]))
        return res


class CaseMString(ExpCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) == 0:
            return False
        if elems[0].type != Lt.mttext:
            return False
        for el in elems:
            if el.type != Lt.mttext:
                return False
        return True
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = []
        i = -1
        if elems[0].text[:3] in ' """ ``` \'\'\' ':
            elems[0].text = elems[0].text[3:]
        for el in elems:
            i += 1
            if el.type == Lt.mttext:
                res.append(el.text)
        res = MString(''.join(res))
        # dprint('## MString')
        return res

class CaseVar(ExpCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) > 1:
            return False
        if elems[0].type == Lt.word:
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value from context by var name'''
        expr = VarExpr(Var(elems[0].text, TypeAny())) # Any for non-typed vars
        return expr

class CaseVar_(ExpCase):
    ''' _ var
        null-assign var
        value won't assigned
    '''
    def match(self, elems:list[Elem]) -> bool:
        # if len(elems) > 1:
        #     return False
        # if elems[0].type == Lt.word and elems[0].text == '_':
        return len(elems) > 1 and isLex(elems[0], Lt.word, '_')
        #     return True
        # return False
    
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


class CaseSeq(SubCase):
    ''' sequence of expressions in one line '''
    
    def __init__(self, delim=' '):
        self.delim = delim
        self.brs = {'(':')', '[':']', '{':'}'}
        self.opens = self.brs.keys()
        self.closs = self.brs.values()

    def match(self, elems:list[Elem]) -> bool:
        # parents = []
        prels('CaseSeq.match %s'% self.delim, elems)
        obr = 0 # bracket counter
        # check without control of nesting, just count open and close brackets
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
            if ee.text == self.delim:
                return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        res = []
        sub = []
        obr = 0
        start = 0
        for i in range(len(elems)):
            ee = elems[i]
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
            if ee.type == Lt.oper and ee.text == self.delim:
                sub = elems[start: i]
                prels('# start= %d, i= %d sub:' % (start, i), sub)
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

def findLastBrackets(elems:list[Elem]):
    ''' return index of opening of last brackets in explession '''
    lem = len(elems)
    inBr = 0
    obrs = '( [ {'.split(' ')
    cbrs = ') ] }'.split(' ')
    if not isLex(elems[-1], Lt.oper, cbrs):
        # incorrect elems data
        return -1

    for i in range(lem-1, -1, -1):
        ee = elems[i]
        if ee.type != Lt.oper:
            continue
        if isLex(ee, Lt.oper, cbrs):
            # step in brackets
            inBr += 1
            continue
        if isLex(ee, Lt.oper, obrs):
            # step out from brackets
            inBr -= 1
            if inBr == 0:
                return i
            continue
    return -2 # just for debug needs


# def splitLastBrackets(elems:list[Elem]):
#     pass


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

