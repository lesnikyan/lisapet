'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *
from nodes.oper_nodes import *
from nodes.datanodes import *


class CaseAssign(SubCase):
    
    # def __init__(self):
    #     self.left = None # TODO: for uni-mode 
    #     self.right = None
        
    def match(self, elems:list[Elem]) -> bool:
        '''
        abc123 = 123.123
        var1 = foo(123, [1,2,3]), 
        arr[index] = 2
        a,b,c = 1, var1, foo(10, 20) '''
        if elems[0].type != Lt.word:
            return False
        if len(elems) < 2:
            # TODO: need dev for assignment with blocks
            return False
        
        for el in elems:
            # left part
            if el.type == Lt.word:
                continue
            if el.type == Lt.oper and el.text in '[],.:':
                continue
            # found operator
            if el.type == Lt.oper and el.text == '=':
                return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # simple case a = expr
        src = elemStr(elems)
        left:list[Elem] = [] # vars only
        right:list[Elem] = [] # vars, vals, funcs, methods
        # slice
        prels('# OpAsgn split1: ', elems)
        opInd = afterLeft(elems)
        print('Assign-split opInd:', opInd, elems[opInd].text)
        left = elems[:opInd]
        right = elems[opInd+1:]
        # TODO: Implement multi-assign case
        return OpAssign(), [left, right]

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        # waiting: OpAssign, [right]
        print('CaseAssign setSub:',base,  subs)
        lsub = len(subs)
        if lsub % 2 > 0:
            # can be changed after tuple case implementation
            raise InterpretErr('number of sub-expressions for assignment looks incorrect: %d ' % lsub)
        hsize = int (lsub  / 2) # half of size
        left = subs[:hsize]
        right = subs[hsize:]
        print('CaseAssign sesubs L/R:', left, right)
        tl = left
        left = []
        for tex in tl:
            if isinstance(tex, ServPairExpr):
                print('pair tex =  ', tex.left, tex.right)
                left.append(tex.getTypedVar())
            else:
                left.append(tex)
        base.setArgs(left, right)

        return base



operPrior = ('() [] . : , -x !x ~x , ** , * / % , + - ,'
' << >> , < <= > >= -> !>, == != , &, ^ , | , && , ||, <-, = += -= *= /= %=  ')


class CaseBinOper(SubCase):
    '''
    0. match operator case
    1. operators ordering.
    2. split by priority
    3. unfold to execution tree'''
    
    def __init__(self):
        priorGroups = operPrior.split(',')
        self.priorGroups = [[ n for n in g.split(' ') if n.strip()] for g in priorGroups]
        self.opers = [oper for nn in self.priorGroups[:-1] for oper in nn]

    def match(self, elems:list[Elem]) -> bool:
        elen = len(elems)
        inBr = 0
        if elen < 3:
            # exceptions: -2+, --1, -sum(1,2,3)
            return False
        for i in range(elen):
            el = elems[i]
        # for el in elems:
            # skip parts in brackets: math or function calls
            if el.text in '([{':
                inBr += 1
                continue
            if el.text in ')]}':
                inBr -= 1
            if inBr > 0:
                continue
            if el.type != Lt.oper:
                continue
            if i in [0, elen-1]:
                continue 
            # in simple case if we have oper, it's operator case
            if el.text in self.opers:
                return True
        return False
                
    # def expr(self, elems:list[Elem])-> tuple[Expression, Context]:
        
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # print('#a51:', [n.text for n in elems])
        src = elemStr(elems)
        lowesPrior = len(self.priorGroups) - 1
        inBr = 0
        maxInd = len(elems)-1
        obr='([{'
        cbr = ')]}'
        inBrs = [] # brackets which was opened from behind
        prels('~~ CaseBinOper', elems)
        for prior in range(lowesPrior, -1, -1):
            skip = -1
            print('prior=', prior, self.priorGroups[prior] )
            for i in range(maxInd, -1, -1):
                el = elems[i]
                etx = el.text
                # counting brackets from tne end, closed is first
                if etx in cbr:
                    inBrs.append(etx)
                    # print(' >> ',etx)
                    continue
                if etx in obr:
                    last = inBrs.pop()
                    # print(' << ', etx, last)
                    continue
                    # TODO: check equality of brackets pairs (not actual for valid code, because [(]) is invalid )
                if len(inBrs) > 0:
                    continue
                # if el.text == ')':
                #     inBr += 1
                #     continue
                # if el.text == '(':
                #     inBr -= 1
                # if inBr > 0:
                #     continue
                if el.type != Lt.oper:
                    continue
                # TODO: fix unary cases, like: 5 * -3,  7 ** -2, x == ! true, (-12)
                if i > 0 and el.text in ['-', '+', '!', '~'] and elems[i-1].type == Lt.oper and elems[i-1].text not in ')]}':
                    # unary case found, skip current pos
                    continue
                if el.text in self.priorGroups[prior]:
                    # we found current split item
                    print('oper-expr>', '`%s`' % src, elemStr(elems[0:i]), '<(%s)>' % elems[i].text, elemStr(elems[i+1:]))
                    # assigMath = '+= -= *= /= %='
                    # if el.text in assigMath:
                    #     opcase = CaseBinAssign()
                    #     return opcase.split(elems)
                    exp = makeOperExp(el)
                    exp.src = src
                    return exp, [elems[0:i], elems[i+1:]]
        # print('#a52:', [n.text for n in elems])
        # return 1,[[]]
        raise InterpretErr('Matched case didnt find key Item in [%s]' % ','.join([n.text for n in elems]))

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' base - top-level (very right oper with very small priority) 
            subs - left and right parts
        '''
        print('oper-bin seSub', base, subs)
        base.setArgs(subs[0], subs[1])


def makeOperExp(elem:Elem)->OperCommand:
    # TODO: make oper command by cases: math, logical, assign and math+assign, bit operators, brackets
    oper = elem.text
    mathOpers = '+ - * / % ** << >>'.split(' ')
    if oper in mathOpers:
        return OpMath(oper)
    boolOpers = '&& ||'.split(' ')
    if oper in boolOpers:
        return OpBinBool(oper)
    cmpOpers = '== != > < >= < <='.split(' ')
    if oper in cmpOpers:
        return OpCompare(oper)
    btOpers = '& | ^'.split(' ')
    if oper in btOpers:
        return OpBitwise(oper)
    if oper == ':':
        return ServPairExpr()
    if oper == '.':
        return OperDot()
    if oper =='<-':
        return IterAssignExpr() # TODO: could be extended for additional cases
    # undefined case:
    raise InterpretErr('!!>>> appropriate case didnt found for oper `%s`' % oper)
    return OperCommand(elem.text)


# Unary cases 
unaryOpers = '- ! ~'.split(' ')
# oneValExptRx = re.compile('[0-9a-z]+?(\(.*\))?')

class CaseUnar(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        ''' -123, -0xabc, ~num, -sum([1,2,3]), !valid, !foo(1,2,3) '''
        if elems[0].type != Lt.oper or elems[0].text not in unaryOpers:
            return False
        if len(elems) == 2 and elems[1].type in [Lt.num, Lt.word]:
            # fast check for trivial cases: -1, !true, ~num, ~ 0xabc
            return True
        # brackets -(... (... (..)))
        inBr = 0
        maxBr = 0
        for ee in elems[1:]:
            if ee.text == '(':
                if inBr == 0 and maxBr > 0:
                    # here we are opening brackets twice
                    # print('# -- opening brackets twice', ee.text)
                    return False
                inBr +=1
                maxBr += 1
                continue
            elif ee.text == ')':
                inBr -=1
                continue
            if inBr == 0 and ee.type == Lt.oper and ee.text not in unaryOpers:
                # not in brackets but found operator after 1-st element
                # except cases with several unary one-by-one: !~x, !-5, ~-(expr)
                # print('# -- not in brackets operator', ee.text)
                return False
        return True
        ## regexp method
        # ss = ''.join([ee.text for ee in elems])
        # return oneValExptRx.match(ss)

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # oper = elems[0].text
        subs = elems[1:]
        expr = makeUnary(elems[0])
        return expr, [subs]

    def setSub(self, base:UnarOper, subs:Expression|list[Expression])->Expression:
        ''' base - unaryExpr
            subs - left part
        '''
        base.setInner(subs[0])
    
    
    # next: BoolNot, BitNot, UnarSign
def makeUnary(elem:Elem)->OperCommand:
    # unaryOpers = '- ! ~'.split(' ')
    oper = elem.text
    if oper == '-':
        return UnarSign(oper)
    if oper == '~':
        return BitNot(oper)
    if oper == '!':
        return BoolNot(oper)


class CaseBrackets(SubCase):
    ''' cases:
        math expression,
        call function
        group any operators
        *cover multiline expressions, like if (one line \n && second line \n || last line )
    '''
    
    def __init__(self):
        pass

    def match(self, elems:list[Elem]) -> bool:
        if elems[0].type != Lt.oper:
            return False
        if elems[0].text == '(' and elems[-1].text == ')':
            # only if other operator cases was failed
            # TODO: test: () smth ()
            return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        base = MultiOper()
        return base, [elems[1:-1]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' base - Multi-oper
            subs - just internal part
        '''
        base.setInner(subs[0])
        return base


class CaseBinAssign(CaseAssign):
    ''' += -= *= /= %=  
    var += val -> var = (var + val)
    
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''  '''
        if elems[0].type != Lt.word or elems[0].text in SPEC_WORDS:
            return False
        afterInd = afterLeft(elems)
        if afterInd == -1:
            return False
        if afterInd > len(elems):
            return False
        elem = elems[afterInd]
        print('CaseBinAssign,split', afterInd, elem.text)
        if elem.type != Lt.oper or elem.text not in EXT_ASSIGN_OPERS:
            return False
        return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' Reusing OpAssign expression object'''
        opIndex = afterLeft(elems)
        biOper = elems[opIndex]
        prels('CaseBinAssign.split1', elems)
        print('biOper:', biOper.text)
        mOper = biOper.text[0] # get math oper, e.g.: + from +=
        left = elems[:opIndex]
        right = elems[opIndex+1:]
        oper = Elem(Lt.oper, mOper)
        asgn = Elem(Lt.oper, '=')
        # new Assign-like sequence: (x += 2) -> (x = x + 2)
        assignElems = left + [asgn] + left + [oper] + right
        return super().split(assignElems)
    
    def setSub(self, base:Expression, subs:list[Expression])->Expression:
        return super().setSub(base, subs)


def checkTypes(elems:list[Elem], exp:list[int]):
    if len(elems) != len(exp):
        return False
    for i in range(len(elems)):
        if elems[i].type != exp[i]:
            return False
    return True


# class _CaseDotOper(SubCase):
    
#     def match(self, elems:list[Elem]) -> bool:
#         '''
#         obj.member
#         obj.member.member.member
#         array[expr].member
#         array[expr].member[key].member
#         array[expr.member].member
#         array[expr].member
#         foo(args).member
#         obj.fmember()
#         obj.fmember(args)
#         foo().bar().baz().member
#         foo().bar().baz().member.member
#         foo().bar().baz().member.method(args)
#         array[foo()].member[key].method()
#         '''
#         if len(elems) < 3:
#             return False
#         return checkTypes(elems, [Lt.word, Lt.oper, Lt.word]) and elems[1].text == '.'

#     def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
#         return OperDot(), [[elems[0]],[elems[2]]]

#     def setSub(self, base:OperDot, subs:Expression|list[Expression])->Expression:
#         print('CaseDotOper:', base, subs)
#         # raise EvalErr('')
#         base.set(subs[0], subs[1])
#         return base


# class CaseColonPair(SubCase):
#     ''' expr : expr '''
    
#     def match(self, elems:list[Elem]) -> bool:
#         if elems[0].type != Lt.oper:
#             return False
#         if elems[0].text == '(' and elems[-1].text == ')':
#             # only if other operator cases was failed
#             # TODO: test: () smth ()
#             return True
#         return False
    
#     def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
#         ''' '''
#         base = MultiOper()
#         return base, [elems[1:-1]]
    
#     def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
#         ''' base - Multi-oper
#             subs - just internal part
#         '''
#         base.setInner(subs[0])
#         return base