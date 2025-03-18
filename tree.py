
"""
"""

from lang import *
from vars import *
from tnodes import *
from oper_nodes import *
from controls import *
from vals import isDefConst, elem2val
from tcases import *
import re
    

class CaseBinAssign(SubCase):
    ''' += -= *= /= %=  '''


class FunCallCase(SubCase):
    ''' foo(agrs)'''
    
    def match(self, elems:list[Elem]) -> bool:
        ''' foo(), foo(a, b, c), foo(bar(baz(a,b,c-d+123)))'''
        if elems[0].type != Lt.word:
            return False
        if elems[1].type != Lt.oper or elems[-1].type != Lt.oper or elems[1].text != '(' or elems[-1].text != ')':
            return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # 1. func name, in next phase: method call: inst.foo() ? separated case for objects with members: obj.field, obj.method()
        # 2. arg-expressions
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        ''' base - FuncExpr '''
        

class CaseArray(SubCase):
    ''' [num, word, expr] '''
    def match(self, elems:list[Elem]) -> bool:
        # TODO: fix match condition
        if elems[0].type == Lt.oper and elems[0].text == '[':
            return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ListExpr()
        return exp, [elems[1:-1]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        for exp in subs:
            base.add(exp)
        return base


class CaseFor(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'for':
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = LoopExpr()
        subs = []
        start = 1
        elen = len(elems)
        for i in range(1, elen):
            prels('>>> %d ' % i, elems[i:])
            ee = elems[i]
            if ee.type == Lt.oper and ee.text == ';':
                subs.append(elems[start:i])
                start = i + 1
            if i == elen - 1 and start < elen - 1:
                # last elem
                print('Last elem')
                subs.append(elems[start:])
        # if start > len(elems) - 1:
        #     subs.append()
        print('# CaseFor.split-', elen,  exp)
        for ees in subs:
            prels('>>', ees)
        return exp, subs
    
    def setSub(self, base:LoopExpr, subs:Expression|list[Expression])->Expression:
        ''' nothing in minimal impl''' 
        slen = len(subs)
        if slen == 1:
            # iterator case
            base.setIter(subs)
        elif slen == 2:
            # pre, cond
            base.setExpr(pre=subs[0], cond=subs[1])
        elif slen == 3:
            # init, cond, post
            base.setExpr(init=subs[0], cond=subs[1], post=subs[2])
        print('# CaseFor.setSub-', base)
        return base


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
            # dev manual impl
            iter = self.iterGen(elems[1:])
        elif CaseArray().match(elems):
            iter = elems2expr(elems)
            # TODO: other iter cases
        return iter

    def iterGen(self, elems:list[Elem]):
        elargs = elems
        if elems[0] == '(':
            elargs = elems[1:-1]
        # TODO: implement usage of Var cases
        argLexems = [ee for ee in elargs if ee.type == Lt.num]
        args = [elem2val(ee) for ee in argLexems]
        start, over, step = 0,0,1
        alen = len(args)
        if alen == 1:
            over = args[0].get()
        elif alen == 2:
            start = args[0].get()
            over = args[1].get()
            over = args[0].get()
        elif alen == 3:
            start = args[0].get()
            over = args[1].get()
            step = args[2].get()
        exp = IterGen(start, over, step)
        return exp
    
    def setSub(self, base:LoopExpr, subs:Expression|list[Expression])->Expression:
        pass

class CaseMatch(BlockCase):
    ''' very specaial case. 
         1. step: match(expr): case 1; case 2: case 3;
         2. case type.
         3. case pattern.
    '''

class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        prels('--DEbug', elems)
        return elems[0].text == '@debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))

expCaseList = [ CaseComment(), CaseDebug(),
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(), CaseIterOper(), CaseMatch(), 
    CaseAssign(), CaseVal(), CaseVar(), CaseBinOper(), CaseBrackets(), CaseUnar()]

def getCases()->list[ExpCase]:
    return expCaseList

def simpleExpr(expCase:ExpCase, elems)->Expression:
    # print('#simple-case:', expCase)
    return expCase.expr(elems)

def complexExpr(expCase:SubCase, elems:list[Elem])->Expression:
    base, subs = expCase.split(elems)
    # print('#complex-case:', expCase)
    # print('#111', subs)
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
    print('#b1', [n.text for n in elems])
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
        print('#code-src: `%s`' % cline.src.src, '$ind=',  indent)
        prels('#cline-code:', cline.code)
        if len(cline.code) == 0:
            continue
        expr = line2expr(cline)
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
                print('lex2tree-pop parents =', parents)
                print('lex2tree-pop curBlock =', curBlock)
        if isinstance(curBlock, IfExpr) and isinstance(expr, ElseExpr):
            # ELSE statement
            curBlock.toElse(expr)
            # TODO: for `else if` case we need additional logic with parent and nested `if` expr
            continue
        if expr.isBlock():
            # start new sub-level
            # if definition of func, type: add to upper level context
            # if isinstance(expr, ElseExpr):
            #     # specific `else` case.
                
            #     # `else if` case need additional logic
            #     continue
            print('!! in-block', parents, curBlock, expr)
            curBlock.add(expr)
            parents.append(curBlock)
            curBlock = expr
            curInd += 1
            continue
        curBlock.add(expr)
        # curBlock.ctx.add(ctx)
        # context?
    return root
