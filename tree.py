
"""
"""

from lang import *
from vars import *
from tnodes import *
from oper_nodes import *
from controls import *
from vals import isDefConst, elem2val, isLex
from tcases import *
import re


class CaseIterOper(SubCase):
    '''
    <- operator is an iterative assignment from collection or iterator to local var
    base use case - for-loop statement
    cases:
    for n <- somearray
    for n <- [1,2,3,5]
    for index, val <- somearray
    for index, _ <- somearray
    for key, val <- {'a':1, 'b':2, 'c':3}
    for key, val <- somedict
    for _, val <- somedict
    for key, _ <- somedict
    for i <- iter(10)
    for _ <- iter(10)
    '''
    def match(self, elems:list[Elem]) -> bool:
        for ee in elems:
            if ee.type == Lt.oper and ee.text == '<-':
                return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        elen = len(elems)
        left, right = [],[]
        for i in range(elen):
            ee = elems[i]
            if ee.type == Lt.oper and ee.text == '<-':
                # fount iter-assignment operator
                left = elems[:i]
                right = elems[i+1:]
                break
        target = []
        for ee in left:
            dest = Var_()
            if not CaseVar_().match([ee]):
                dest = Var(None, left[0].text, Undefined)
            target.append(dest)
        # expMain = IterAssignExpr()
        expAssign = IterAssignExpr()
        expAssign.setTarget(target)
        expIter = self.iterExpr(right)
        expAssign.setIter(expIter)
        return expAssign, []

    def iterExpr(self, elems:list[Elem]):
        ''' make IterAssignExpr by lexems. cases:
            iter(expr)
            expr
            [expr, expr, expr]
            {expr:expr, expr:expr}
        '''
        iter = None
        if elems[0].text == 'iter':
            # dev manual impl with numbers (not vars)
            iter = self.iterGen(elems[1:])
        elif CaseArray().match(elems):
            iter = elems2expr(elems) # TODO: change to returning subs with latest build in class.setSub
            # TODO: other iter cases
        elif len(elems) == 1 and elems[0].type == Lt.word:
            # TODO: varExpr for array-var
            pass
        return iter

    def iterGen(self, elems:list[Elem]):
        elargs = elems
        if elems[0] == '(':
            elargs = elems[1:-1]
        # TODO: implement usage of Var cases iter(var1, var2, var2)
        argLexems = [ee for ee in elargs if ee.type == Lt.num]
        args = [elem2val(ee) for ee in argLexems]
        start, over, step = 0,0,1
        alen = len(args)
        if alen == 1:
            over = args[0].get()
        if alen > 1:
            start = args[0].get()
            over = args[1].get()
        if alen == 3:
            # start = args[0].get()
            # over = args[1].get()
            step = args[2].get()
        exp = IterGen(start, over, step)
        return exp
    
    def setSub(self, base:LoopExpr, subs:Expression|list[Expression])->Expression:
        print('IterOper: ', base, subs)


class CaseMatch(SubCase):
    ''' very specaial case. 
         1. step: match(expr): case 1; case 2: case 3;
         2. case type.
         3. case pattern.
    '''

    def match(self, elems:list[Elem]) -> bool:
        ''' match expr '''
        if len(elems) < 2:
            return False
        if isLex(elems[0], Lt.word, 'match'):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        return MatchExpr(), [elems[1:]]


    def setSub(self, base:MatchExpr, subs:list[Expression])->Expression:
        base.setMatch(subs[0])
        return base


class _CaseCase(SubCase):
    ''' Sub element of CaseMatch '''

    def match(self, elems:list[Elem]) -> bool:
        ''' 
        first sub-level into match block
        expr -> expr '''
        if len(elems) < 3:
            return False
        
        if isLex(elems[0], Lt.word, ''):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        subs = elems[1:]
        

    def setSub(self, base:Expression, subs:list[Expression])->Expression:
        pass

class RawCase:
    ''' case we need do some post-operation '''

class ArrOper(RawCase):
    def __init__(self, left=None, right=None):
        self.left:Expression = left
        self.right:Expression = right

def findOper(elems:list[Elem], oper:str):
    ''' find first oper between words and brackets'''

    inBr = 0
    obr = '([{'
    cbr = '}])'
    
    for i in range(len(elems)):
        ee = elems[i]
        # if ee.type != Lt.oper:
        #     continue
        if ee.type == Lt.oper and ee.text in obr:
            inBr += 1
            continue
        if ee.type == Lt.oper and ee.text in cbr:
            inBr -= 1
            continue
        if inBr:
            continue
        if ee.text == oper:
            return i
        if i > 0:
            return i
    return -1
    

class CaseArrowR(SubCase):
    ''' multi pattern 
        1. lambda case
            \arg -> expr
        2. case of match:
            expr -> expr
        3. put elem to collection (?)
            12 -> array
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''
        expr -> expr '''
        if len(elems) < 2:
            return False
        oper = '->'
        oind = findOper(elems, oper)
        print('# match-found: ', oind)
        if oind < 1:
            return False
        
        return elems[oind].text == oper

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        arrInd = findOper(elems, '->')
        exp = ArrOper()
        subs = [elems[:arrInd], elems[arrInd+1:]]
        return exp, subs

    def setSub(self, base:ArrOper, subs:list[Expression])->Expression:
        base.left = subs[0]
        if len(subs) > 1 and isinstance(subs[1], Expression):
            base.right = subs[1]
    


class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        prels('--DEbug', elems)
        return elems[0].text == '@debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))

expCaseList = [ CaseComment(), CaseDebug(),
    CaseFuncDef(),
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(), CaseIterOper(), CaseMatch(), CaseArrowR(),
    CaseSemic(), CaseAssign(), CaseBinAssign(),
    CaseArray(), CaseCollectElem(), CaseFunCall(),
    CaseVar_(), CaseVal(), CaseVar(), CaseBinOper(), CaseBrackets(), CaseUnar()]

def getCases()->list[ExpCase]:
    return expCaseList

def simpleExpr(expCase:ExpCase, elems)->Expression:
    # print('#simple-case:', expCase)
    return expCase.expr(elems)

def complexExpr(expCase:SubCase, elems:list[Elem])->Expression:
    base, subs = expCase.split(elems)
    # print('#complex-case:', expCase)
    print('#complexExpr', base, subs)
    if isinstance(subs, list):
        for ee in subs:
            prels('#cml-exp1:', ee)
    if not expCase.sub():
        return base
    if not subs or not subs[0]:
        return base
    subExp:list[Expression] = []
    for sub in subs:
        prels('#complexExpr1:', sub)
        texpr = elems2expr(sub)
        subExp.append(texpr)
    expCase.setSub(base, subExp)
    return base

def makeExpr(expCase:ExpCase, elems:list[Elem])->Expression:
    # print('#b2', [n.text for n in elems])
    if expCase.sub():
        return complexExpr(expCase, elems)
    return simpleExpr(expCase, elems)

def elems2expr(elems:list[Elem])->Expression:
    print('#elems2expr #b1', [n.text for n in elems])
    for expCase in getCases():
        if expCase.match(elems):
            # if expCase.sub():
            #     return complexExpr(expCase, elems)
            # print('#c foundCase:', expCase.__class__.__name__)
            expr = makeExpr(expCase, elems)
            # print('#b5', expr)
            return expr
    raise InerpretErr('No current ExprCase for `%s` ' % '_'.join([n.text for n in elems]))


def line2expr(cline:CLine)-> Expression:
    ''' '''
    # types: assign, just value, definition, definition content (for struct), operator, func call, control (for, if, func, match, case), 
    expr = elems2expr(cline.code)
    return expr

def raw2done(parent:Expression, raw:RawCase)->Expression:
    # match-case
    print('>> raw2done', parent, raw)
    if isinstance(parent, MatchExpr) and isinstance(raw, ArrOper):
        # `case` sub-expr in `match`
        res = CaseExpr()
        res.setExp(raw.left)
        if raw.right:
            # one-line case
            res.add(raw.right)
        return res
    # lambdas ...
    
    

def lex2tree(src:list[CLine]) -> Block:
    ''' '''
    root = Module()
    curBlock = root
    parents:list[Block] = []
    curInd = 0 # indent
    print('~~~~~~~~~~~` start tree builder ~~~~~~~~~~~~')
    for cline in src:
        print('  -  -  -')
        indent = cline.indent
        print('#code-src: `%s`' % cline.src.src, '$ind=',  indent, '; curInd=', curInd)
        prels('#cline-code:', cline.code)
        if len(cline.code) == 0:
            continue
        expr = line2expr(cline)
        
        
        # print('lex2tree-14:', expr, expr.__class__.__name__, type(expr))
        if isinstance(expr, CaseComment):
            # nothing for comment now
            continue
        print('lex2tree-2 expr:', expr, '; parents:', parents, curBlock)
        if indent < curInd:
            # end of block
            stepsUp = curInd - indent
            print('-- ind:', curInd, indent)
            if isinstance(expr, ElseExpr):
                # the same indent/parent level as `if` opener
                stepsUp -= 1
            print('lex2tree-3#stepsUp=', stepsUp, parents)
            for _ in range(stepsUp):
                curBlock = parents.pop()
                curInd -= 1
                print('lex2tree-pop parents =', parents)
                print('lex2tree-pop curBlock =', curBlock)
                
        if isinstance(expr, RawCase):
            expr = raw2done(curBlock, expr)
            print('>> after raw:', expr)
            
        if isinstance(curBlock, IfExpr) and isinstance(expr, ElseExpr):
            # ELSE statement
            curBlock.toElse(expr)
            # TODO: for `else if` case we need additional logic with parent and nested `if` expr
            continue
        # print('lex2tree-4:', expr, expr.__class__.__name__, type(expr))
        stepBlock = expr.isBlock()
        # if stepBlock:
        #     if isinstance(expr, CaseExpr):
        #         # can be 1-line
        #         # if 1-line, it just will be reset by next case line 
        #         if not expr.block.isEmpty():
        #             stepBlock = False
        
        if stepBlock:
            # start new sub-level
            # if definition of func, type: add to upper level context
            # if isinstance(expr, ElseExpr):
            #     # specific `else` case.
                
            #     # `else if` case need additional logic
            #     continue
            # print('!! in-block', parents, curBlock, expr)
            curBlock.add(expr)
            parents.append(curBlock)
            curBlock = expr
            curInd += 1
            print('-=-= indent cur:', curInd)
            continue
        curBlock.add(expr)
        # curBlock.ctx.add(ctx)
        # context?
    return root
