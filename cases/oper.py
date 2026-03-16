'''
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.utils import *
from cases.tcases import *
from nodes.oper_nodes import *
from nodes.func_opers import FuncApplyOper
from nodes.datanodes import *


class CaseAssign(SubCase):

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
        # prels('# OpAsgn split1: ', elems)
        opInd = afterLeft(elems)
        # dprint('Assign-split opInd:', opInd, elems[opInd].text)
        left = elems[:opInd]
        right = elems[opInd+1:]
        # TODO: Implement multi-assign case
        expr = OpAssign()
        expr.src = elems
        return expr, [left, right]

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        # waiting: OpAssign, [right]
        # print('CaseAssign setSub:',base,  subs)
        lsub = len(subs)
        if lsub % 2 > 0:
            # can be changed after tuple case implementation
            raise InterpretErr('number of sub-expressions for assignment looks incorrect: %d ' % lsub)
        hsize = int (lsub  / 2) # half of size
        left = subs[:hsize]
        right = subs[hsize:]
        # dprint('CaseAssign sesubs L/R:', left, right)
        tl = left
        left = []
        for tex in tl:
            if isinstance(tex, ServPairExpr):
                # dprint('pair tex =  ', tex.left, tex.right)
                left.append(tex.getTypedVar())
            else:
                left.append(tex)
        base.setArgs(left, right)

        return base


_operPrior = ('() [] {} , . , ~> , ... , -x ! ~ , ** ^/ , * / % , + - ,'
' << >> , =~ ?~ /~, < <= > >= !> ?> !?>, == != , &, ^ , | , ::, && , ||, $, ?: , : , ?, \\ , -> , .. , <- , = += -= *= /= %= , ; , !: :? , /: ') #

_noOpers = ['\\', '->', '.', ',' ,';']

class CaseBinOper(SubCase):
    '''
    0. match operator case
    1. operators ordering.
    2. split by priority
    3. unfold to execution tree'''
    
    def __init__(self):
        priorGroups = _operPrior.split(',')
        self.priorGroups = [[ n for n in g.split(' ') if n.strip()] for g in priorGroups]
        self.opers = [oper for nn in self.priorGroups[:] for oper in nn]
        self.splitter = None
        # self.funcCall = CaseFunCall()
        self.lastM = -1

    def match(self, elems:list[Elem], ind=-1) -> bool:
        # print('CaseBinOper.match', elemStr(elems))
        if ind == 0:
            return False
        elen = len(elems)
        # inBr = 0
        if elen < 3:
            return False
        main = ind
        if ind < 0:
            if self.splitter is None:
                self.splitter = OperSplitter.getInst()
            main = self.splitter.mainOper(elems, lesser='**')
        res =  main > 0 and elems[main].text not in _noOpers and isLex(elems[main], Lt.oper, self.opers)
        self.lastM = main if res else -1
        return res

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        main = self.lastM
        # if main == -1:
        #     main = self.splitter.mainOper(elems)
        exp = makeOperExp(elems[main])
        src = elemStr(elems)
        exp.src = src
        return exp, [elems[0:main], elems[main+1:]]

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' base - top-level (very right oper with very small priority) 
            subs - left and right parts
        '''
        # dprint('oper-bin seSub', base, subs)
        base.setArgs(subs[0], subs[1])
        return base


mathOpers = '+ - * / % ** ^/'.split(' ')
boolOpers = '&& ||'.split(' ')
cmpOpers = '== != > < >= < <='.split(' ')
btOpers = '& | ^ << >>'.split(' ')
binAssgn = '+= -= *= /= %='.split(' ')

def makeOperExp(elem:Elem)->OperCommand:
    # TODO: make oper command by cases: math, logical, assign and math+assign, bit operators, brackets
    oper = elem.text
    if oper in mathOpers:
        return OpMath(oper)
    if oper in boolOpers:
        return OpBinBool(oper)
    if oper in cmpOpers:
        return OpCompare(oper)
    if oper in btOpers:
        return OpBitwise(oper)
    if oper == '=':
        return OpAssign()
    if oper in binAssgn:
        return OpBinAssign(oper)
    if oper == ':':
        return ServPairExpr()
    if oper == '?':
        return TernarExpr()
    if oper == '?:':
        return FalseOrExpr()
    if oper == '::':
        return IsTypeExpr()
    if oper == '?>':
        return IsInExpr()
    if oper == '!?>':
        return IsInExpr(isNot=True)
    # if oper == '.':
    #     return OperDot()
    if oper == '=~':
        return RegexpMatchOper()
    if oper == '?~':
        return RegexpSearchOper()
    if oper == '..':
        return TwoDotsOper()
    if oper =='<-':
        return LeftArrowExpr() # TODO: could be extended for additional cases
        # return IterAssignExpr() # TODO: could be extended for additional cases
    if oper == '$':
        return FuncApplyOper()
    # undefined case:
    raise InterpretErr('!!>>> appropriate case didnt found for oper `%s`' % oper)
    # return OperCommand(elem.text)


# Unary cases 
unaryOpers = '- ! ~'.split(' ')
# oneValExptRx = re.compile('[0-9a-z]+?(\(.*\))?')

class CaseLUnar(SubCase):
    ''' Left unary operators
    -n ; ~n ; !n
    '''
    def __init__(self, strformat=None):
        super().__init__()
        self.formatter:SFormatter = strformat
    
    def match(self, elems:list[Elem]) -> bool:
        ''' -123, -0xabc, ~num, -sum([1,2,3]), !valid, !foo(1,2,3) '''
        lem = len(elems)
        if lem < 2:
            return False
        if elems[0].type != Lt.oper or elems[0].text not in unaryOpers:
            return False
        if lem == 2 and elems[1].type in [Lt.num, Lt.word]:
            # fast check for trivial cases: -1, !true, ~num, ~ 0xabc
            return True
        # brackets -(... (... (..)))
        
        # return isSolidExpr(elems[1:], skipKeywords=True)
        # print('UO$14', r)
        inBr = 0
        maxBr = 0
        # for ee in elems[1:]:
        for i in range(1, lem):
            ee = elems[i]
            if ee.text == '(':
                if inBr == 0 and maxBr > 0:
                    # here we are opening brackets twice
                    # dprint('# -- opening brackets twice', ee.text)
                    return False
                inBr +=1
                maxBr += 1
                continue
            elif ee.text == ')':
                inBr -=1
                continue
            if inBr:
                continue
            if ee.type == Lt.oper and ee.text not in unaryOpers:
                # not in brackets but found operator after 1-st element
                # except cases with several unary one-by-one: !~x, !-5, ~-(expr)
                # dprint('# -- not in brackets operator', ee.text)
                return False
        return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # oper = elems[0].text
        subs = elems[1:]
        expr = makeUnary(elems[0])
        return expr, [subs]

    def setSub(self, base:UnarOper, subs:Expression|list[Expression])->Expression:
        ''' base - unaryExpr
            subs - left part
        '''
        sub = subs[0]
        # dprint('Unar.setSub', base, sub)
        
        # TODO: it breaks normal interpret behaviour, think about it
        if self.formatter and isinstance(sub, (StringExpr)) and isinstance(base, BitNot):
            # FString detected
            base = self.formatter.formatString(sub.get().getVal())
        else:
            base.setInner(sub)
        return base

    
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


class CaseBrackets(SubCase, SolidCase):
    ''' cases:
        math expression,
        call function
        group any operators
        *cover multiline expressions, like if (one line \n && second line \n || last line )
    '''
    
    def __init__(self):
        pass

    def match(self, elems:list[Elem], ind=None) -> bool:
        if elems[0].type != Lt.oper or elems[-1].type != Lt.oper:
            return False
        if elems[0].text != '(' or elems[-1].text != ')':
            # only if other operator cases was failed
            return False
        return True
        # r =  isSolidExpr(elems, getLast=True, skipKeywords=True)
        # if not isinstance(r, tuple):
        #     return False
        # ok, pos = r
        # return ok and pos == 0
        # if not ok or pos != 0:
        #     return False
        # return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        base = MultiOper()
        base.src = elemStr(elems)
        return base, [elems[1:-1]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' base - Multi-oper
            subs - just internal part
        '''
        # print('()case', base, subs)
        base.setInner(subs[0])
        return base


def checkTypes(elems:list[Elem], exp:list[int]):
    if len(elems) != len(exp):
        return False
    for i in range(len(elems)):
        if elems[i].type != exp[i]:
            return False
    return True


class CaseListGen(SubCase, SolidCase):
    ''' [startVal..endVal] '''
    
    def __init__(self):
        super().__init__()
        self.cs = CaseSeq('..')
    
    def match(self, elems:list[Elem]) -> bool:
        # trivial check
        # TODO: add check for complex cases like [] + []
        # if isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'):
        #     return True
        
        if not isLex(elems[-1], Lt.oper, ']'):
            return False
        # opInd = findLastBrackets(elems)
        # if opInd != 0:
        #     return False
        # r =  isSolidExpr(elems, getLast=True, skipKeywords=True)
        # if not isinstance(r, tuple):
        #     return False
        # ok, pos = r
        # if not ok:
        #     return False
        return self.cs.match(elems[1:-1])

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[1:-1]
        # cs = CaseSeq('..')
        subs = [sub]
        if self.cs.match(sub):
            _, subs = self.cs.split(sub)
        exp = ListGenExpr()
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # dprint('ListGenExpr.setSub: ', base, subs)
        base.setArgs(*subs)
        return base


class CaseListComprehension(SubCase, SolidCase):
    '''
    List comprehantion. As possible used haskell-like syntax.
    We don`t use verticall bar (| as haskell) because it olready is used as a bitwise OR with another precedence.
    Semicolon (;) is used for split internal sub-parts instead.
    cases:
    [x ; x <- listVar] # just one-2-one copy Case0
    [ x + 2 ; x <- [a .. b]] # with simple modificator of each element Case1
    # with filtering conditions. Last sub-part will be an condition of filter. Case2
    [ x ; x <- listVar ; x > 5 ] 
    [ x ; x <- listVar ? x > 5 ]
    # with declaration part. Case3
    [ x ; x <- listVar ; y = x ** 2, z = 2 * x ; x + y > 100 && y - z < 1000 ] # comma bitween assignments (declined, wrong precedens)
    [ x ; x <- listVar ; y, z = x ** 2 , 2 * x ; x + y > 100 && y - z < 1000 ] # multiassignment (for next gen assignment of left-tuple)
    
    [x + y ; x <- list1, y <- list2 ; x != y] # several iterators next in loop of prev. Case3

    # to think # flatten list of lists [[1],[2,3],[4,5]] -> [1,2,3,4,5]
    [x ; (sub <- listOfLists) x <- sub ;  len(sub) > 3] 
    [x ; x <- [sub <- listOfLists] ; len(sub) > 2] # nested iterators
    [x ; sub <- listOfLists ; x <- sub ; len(sub) > 2] # if next part is iterator - run loop
    [x ; sub <- listOfLists , x <- sub ; len(sub) > 2] # the same as Case3 ??
     '''
    
    def __init__(self):
        super().__init__()
        self.spl = OperSplitter.getInst()
        self.cs = CaseSemic()
         
    def match(self, elems:list[Elem]) -> bool:
        
        if len(elems) < 7:
            return False
        if not (isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']') ):
            return False
        
        # opInd = findLastBrackets(elems)
        # if opInd != 0:
        #     return False
        
        
        # opInd = self.spl.mainOper(elems)
        # if opInd != 0:
        #     return False
        # subElems = elems[1:-1]
        # opInd = self.spl.mainOper(subElems)
        return self.cs.match(elems[1:-1])
        # return opInd > 0 and subElems[opInd].text == ';'

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[1:-1]
        # subs = []
        # if self.cs.match(sub):
        #     _, subs = self.cs.split(sub)
        # subs = []
        _, subs = self.cs.split(sub)
        exp = ListComprExpr()
        subs = [s for s in subs if len(s)]
        # prels('LC.elems = :', elems, show=1) 
        # prels('ListComr subs=', subs, show=1)
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # dprint('CaseListComprehension.setSub: ', base, subs)
        base.setInner(subs)
        return base

_inline_contr_keyws = ['if','for','while']

class CaseInlineSub(SubCase):
    ''' 1-line sub-block
        control /:  expr 
        
        if x < b /: print(a)
        for n <- nums /: x = foo(n)
        
        # complex:
        if a = foo(b); a < 10 /: res <- b
        for i <- [1..100] /: if i % 2 != 0 /: x = foo(i); res <- x; print(x)
        x -> (for i <- nums /: res <- i * 10)
        '''
    
    def __init__(self):
        super().__init__()
        self.spl = OperSplitter.getInst()
        self.lastId = None
    
    def match(self, elems:list[Elem]) -> bool:
        # print('Case /: >>')
        self.lastId = None
        if len(elems) < 3:
            return False
        
        if not isLex(elems[0], Lt.word, _inline_contr_keyws):
            return False

        main = self.spl.mainOper(elems, lesser='/:')
        self.lastId = main
        return elems[main].text == '/:'
        
        # return isLex(elems[main], Lt.oper, '/:')

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # dprint('CaseInlineSub split', elems)
        # idx = self.spl.mainOper(elems)
        idx = self.lastId
        ctrl = elems[:idx]
        sub = elems[idx+1:]
        # print('', elemStr(ctrl), '<<%s>>' % elems[idx].text, elemStr(sub))
        exp = CtrlSubExpr()
        return exp, [ctrl, sub]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' '''
        # dprint('CaseInlineSub seSub', base, subs)
        base.setArgs(subs[0], subs[1])
        return base
