'''
ExpCases here for exec tree
'''

from lang import *
from vars import *
from tnodes import *
from oper_nodes import *
from controls import *
from vals import isDefConst, elem2val, isLex


SPEC_WORDS = 'for while if else func type def struct var match case'.split(' ')
EXT_ASSIGN_OPERS = '+= -= *= /= %='.split(' ')


def afterLeft(elems:list[Elem])->int:
    ''' find index of elem after var, vars and possible brackets of collections elem
    cases:
        var ...
        a, b, c ...
        arr[expr] ... 
    '''
    res = 0
    inBr = 0
    opers = ''.split('= += -= *= /= %=')
    for i in range(len(elems)):
        ee = elems[i]
        if inBr:
            if ee.text == ']':
                # close brackets
                inBr -= 1
            continue
        if ee.type == Lt.oper and  ee.text == '[':
            # enter into brackets
            inBr += 1
            continue
        if i > 0 and ee.type != Lt.word and (ee.type == Lt.oper and ee.text != ','):
            res = i
            break
    return res

def afterNameBr(elems:list[Elem])->int:
    ''' find index of elem after var/func Name and possible brackets
    cases:
        var ...
        foo(arg, arg, arg) ...
        arr[expr] ... 
    '''
    res = 0
    inBr = ''
    obr = '([{'
    cbr = ')]}'
    for i in range(len(elems)):
        ee = elems[i]
        # if inBr:
        if ee.text in cbr :
            # print('#close', ee.text)
            if obr.index(inBr[-1]) != cbr.index(ee.text):
                print('# ee:', ee.text, 'inbr:', inBr)
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
            # print('#open:', inBr)
            continue
        if inBr:
            continue
        if i > 0:
            res = i
            break
    return res
    

def prels(pref, elems:list[Elem]):
    print(pref, [n.text for n in elems])


class ExpCase:
    ''' '''
    def match(self, elems:list[Elem])-> bool:
        pass
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        pass
    
    def sub(self)->list[Elem]:
        return None
    
    # def setSub(self, expr:Expression):
    #     pass

'''
Cases:
Val: 123, 'asd', true, null
Var: name,  
Func: foo(), foom(expr), bar(baz(arg, arg))
Oper: a + b, age(user) < 45
Obj: obj.field, obj.foo()
if expr && expr2
for n <- expr
type Abc list[str] # ?
type User struct name:str, age: int # ?
struct User ...
'''


class CaseComment(ExpCase):
    ''' possibly will be used for meta-coding'''
    def match(self, elems:list[Elem])-> bool:
        s = ''.join([n.text for n in elems]).lstrip()
        # print('#== CaseComment.match:', s)
        return s.startswith('#')
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        CommentExpr(''.join([n.text for n in elems]).lstrip())


class CaseVal(ExpCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) > 1:
            return False
        # print('#a8: ', [n.text for n in elems])
        # print('#a8: ', [Lt.name(n.type) for n in elems])
        # if elems[0].type not in [Lt.word, Lt.num, Lt.text]:
        #     return False
        if elems[0].type in [Lt.num, Lt.text]:
            # print('#a9')
            return True
        # if elems[0].type == Lt.word and isDefConst(elems[0].text):
        #     return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = ValExpr(elem2val(elems[0]))
        # print('## CaseVal')
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
        expr = VarExpr(Var(None, elems[0].text)) # TODO: try to define a type
        return expr

class CaseVar_(ExpCase):
    ''' _ var
        null-assign var
        value won't assigned
    '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) > 1:
            return False
        if elems[0].type == Lt.word and elems[0].text == '_':
            return True
        return False
    
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
        # print('#a5::', [n.text for n in elems])
        # print('#a5::', [Lt.name(n.type) for n in elems])
        if elems[0].type != Lt.word:
            return False
        if len(elems) < 2:
            # TODO: need dev for assignment with blocks
            return False
        
        for el in elems:
            # left part
            if el.type == Lt.word:
                continue
            if el.type == Lt.oper and el.text == ',':
                continue
            # found operator
            if el.type == Lt.oper and el.text == '=':
                return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # simple case a = expr
        left:list[Elem] = [] # vars only
        right:list[Elem] = [] # vars, vals, funcs, methods
        # slice
        prels('# OpAsgn split1: ', elems)
        # for i, el in enumerate(elems):
        #     if el.type != Lt.oper or el.type == Lt.space or el.text != '=':
        #         # left.append(el)
        #         continue
        #     # = found
        #     left = elems[0:i]
        #     if len(elems) > i:
        #         # `=` not last
        #         right = elems[i+1:]
        # left = [el for el in left if el.type != Lt.space]
        opInd = afterLeft(elems)
        print('Assign-split opInd:', opInd, elems[opInd].text)
        left = elems[:opInd]
        right = elems[opInd+1:]
        # TODO: Implement multi-assign case
        if len(left) == 1:
            dest = Var_()
            if not CaseVar_().match(left):
                dest = Var(None, left[0].text, Undefined)
            expr = OpAssign(dest,None) 
            return expr, [right]
        # if collection[index]
        if isLex(left[1], Lt.oper, '['):
            expr = OpAssign(None,None)
            return expr,[left, right]

        # print('#a50:', [n.text for n in elems])
        return 2,[[]]
        
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        # waiting: OpAssign, [right]
        # print('#b4', subs)
        left = subs[:-1]
        right = subs[-1]
        base.right = right
        if len(left) == 1:
            base.left = left
        else:
            # multi-assignment
            pass
        return base



operPrior = ('() [] . , -x !x ~x , ** , * / % , + - ,'
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
        self.opers = [oper for nn in self.priorGroups for oper in nn]

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
        lowesPrior = len(self.priorGroups) - 1
        inBr = 0
        maxInd = len(elems)-1
        obr='([{'
        cbr = ')]}'
        inBrs = [] # brackets which was opened from behind
        # prels('~~ CaseBinOper', elems)
        for prior in range(lowesPrior, -1, -1):
            skip = -1
            # print('prior=', prior, self.priorGroups[prior] )
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
                    exp = makeOperExp(el)
                    return exp, [elems[0:i], elems[i+1:]]
        # print('#a52:', [n.text for n in elems])
        # return 1,[[]]
        raise InerpretErr('Matched case didnt find key Item in [%s]' % ','.join([n.text for n in elems]))

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' base - top-level (very right oper with very small priority) 
            subs - left and right parts
        '''
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
    # undefined case:
    return OperCommand(elem.text)


# Unary cases 
unaryOpers = '- ! ~'.split(' ')
# oneValExptRx = re.compile('[0-9a-z]+?(\(.*\))?')

class CaseUnar(SubCase):
    def match(self, elems:list[Elem]) -> bool:
        ''' -123, -0xabc, ~num, -sum([1,2,3]), !valid, !foo(1,2,3) '''
        # print('#unaryOpers ',unaryOpers)
        # prels('#unary-match1: ', elems)
        if elems[0].type != Lt.oper or elems[0].text not in unaryOpers:
            # print('# -- not in unaryOpers', elems[0].text)
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


class BlockCase(ExpCase):
    ''' control sub and inner sub 
        function, for-loop, if-statement, match-case statement
    '''

class CaseIf(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'if':
            return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = IfExpr()
        return exp, [elems[1:]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        base.setCond(subs[0])
        return base


class CaseWhile(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'while':
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = WhileExpr()
        return exp, [elems[1:]]

    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression: 
        base.setCond(subs[0])
        return base


class CaseElse(BlockCase, SubCase):
    ''' 
    in base impl no else with sub condition:
    if cond
        code
    else
        if cond
            code
        else
            code
    
    '''
        
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'else':
            # TODO: possible case in feature: else if sub-cond
            return True
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ElseExpr()
        return exp,[elems[1:]]
    
    def setSub(self, base:Expression, subs:Expression|list[Expression])->Expression:
        ''' nothing in minimal impl''' 
        # base.setCond(subs[0])
        return base



class CaseSeq(ExpCase):
    ''' sequence of expressions in one line '''
    
    def __init__(self, delim=' '):
        self.delim = delim
        self.brs = {'(':')', '[':']', '{':'}'}
        self.opens = self.brs.keys()
        self.closs = self.brs.values()

    def match(self, elems:list[Elem]) -> bool:
        # parents = []
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
                # if len(sub) == 0:
                #     continue
                res.append(sub)
                # sub = []
                continue
            # sub.append(ee)
        # print('Seq.split, start =', start, 'len-elems =', len(elems))
        if start < len(elems):
            # print('- - post-append')
            res.append(elems[start:])
        return None, res


class CaseSemic(CaseSeq, SubCase):
    ''' Semicolons out of controls cases. The same as one-line block
        a=5; b = 7 + foo(); c = a * b
        uses if not control structure like: if, for, etc
    '''

    def __init__(self):
        super().__init__(';')

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        print('IterOper: ', base, subs)


class CaseCommas(CaseSeq):
    ''' a, b, foo(), 1+5  '''
    def __init__(self):
        super().__init__(',')


class CaseColon(CaseSeq):
    ''' key: val  '''
    def __init__(self):
        super().__init__(':')


class CaseArray(SubCase):
    ''' [num, word, expr] '''

    def match(self, elems:list[Elem]) -> bool:
        # trivial check
        # TODO: add check for complex cases like [] + []
        if isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'):
            return True
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ListExpr()
        sub = elems[1:-1]
        cs = CaseCommas()
        subs = [sub]
        if cs.match(sub):
            _, subs = cs.split(sub)
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        print('CaseArray.setSub: ', base, subs)
        for exp in subs:
            base.add(exp)
        return base

class CaseCollectElem(SubCase):
    ''' 
    case array[index-expr]
    case dict[key-expr]
    usage:
    get: a = arr[expr]; 
    set: arr[expr] = expr
    varName_Expression [ indexVal_Expression ]
    [] - access to array operator
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''
        simplest: varName[indexVar|intVal]
        elems[0]: varName, funcName + (expr), 
        more complex: obj.field, obj.method(expr)
        '''
        prels('CaseCollectElem.match1', elems)
        opIndex = afterNameBr(elems)
        oper = elems[opIndex]
        print('CaseCollectElem, oper =', oper.text, 'index=', opIndex)
        if opIndex == -1 and isLex(elems[-1], Lt.oper, ']'):
            # case: var[key]
            return True
        
        if len(elems) < 4:
            return False
        # assign to no-key case var[] = 123
        
        # simple case: varName [ any ]
        if len(elems) == 4 and elems[0].type == Lt.word and isLex(elems[1], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']'):
            # check internal brackets to avoide a[]...b[]
            return True
        # TODO: match complex cases: var.meth(arg, arg, arg)[foo(var.field + smth) - arr[index + var]]
        
        return False

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        '''
        execution plan:
        1. get Var in context
        2. eval key|index expr
        3. get val from collection by index|key
        '''
        varElems = []
        keyElems = []
        for ee in elems:
            if isLex(ee, Lt.oper, '['):
                keyElems = elems[len(varElems)+1: -1]
                break
            varElems.append(ee)
        exp = CollectElemExpr()
        return exp, [varElems, keyElems]
            
    def setSub(self, base:CollectElemExpr, subs:Expression|list[Expression])->Expression:
        base.setVarExpr(subs[0])
        base.setKeyExpr(subs[1])
        return base


class CaseBinAssign(CaseAssign):
    ''' += -= *= /= %=  
    var += val -> var = (var + val)
    
    '''

    def match(self, elems:list[Elem]) -> bool:
        '''  '''
        if elems[0].type != Lt.word or elems[0].text in SPEC_WORDS:
            return False
        afterInd = afterNameBr(elems)
        # prels('>>>', elems)
        # print('=== afterInd:', afterInd)# , elems[afterInd].text)
        if afterInd == -1:
            return False
        elem = elems[afterInd]
        if elem.type != Lt.oper or elem.text not in EXT_ASSIGN_OPERS:
            return False
        return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' Reusing OpAssign expression object'''
        opIndex = afterNameBr(elems)
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


class CaseFor(BlockCase, SubCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if elems[0].text == 'for':
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
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
        exp:LoopBlock = None
        match len(subs):
            case 1: exp = LoopIterExpr()
            case 2|3: exp = LoopExpr()
            case _ :pass
        print('# CaseFor.split-', elen,  exp, 'len-subs=', len(subs))
        for ees in subs:
            prels('>>', ees)
        return exp, subs
    
    def setSub(self, base:LoopExpr, subs:Expression|list[Expression])->Expression:
        ''' nothing in minimal impl''' 
        slen = len(subs)
        print('# CaseFor.setSub-', slen, subs)
        match slen:
            # iterator case
            case 1 if isinstance(base, LoopIterExpr): base.setIter(subs[0])
            # pre, cond
            case 2 if isinstance(base, LoopExpr): base.setExpr(pre=subs[0], cond=subs[1])
            # init, cond, post
            case 3 if isinstance(base, LoopExpr): base.setExpr(init=subs[0], cond=subs[1], post=subs[2])
        print('# CaseFor.setSub-', base)
        return base


class CaseFuncDef(BlockCase, SubCase):
    ''' func foo(arg-expressions over comma) '''
    def match(self, elems:list[Elem]) -> bool:
        if isLex(elems[0], Lt.word, 'func'):
            return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' func name (arg, arg, arg, ..) '''
        fname = elems[1].text
        sub = elems[3:-1]
        cs = CaseCommas()
        subs = [sub]
        if cs.match(sub):
            _, subs = cs.split(sub)
        func = FuncDefExpr(fname)
        return func, subs
    
    def setSub(self, base:FuncDefExpr, subs:Expression|list[Expression])->Expression:
        for exp in subs:
            base.addArg(exp)

class CaseFunCall(SubCase):
    ''' foo(agrs)'''

    def match(self, elems:list[Elem]) -> bool:
        ''' foo(), foo(a, b, c), foo(bar(baz(a,b,c-d+123)))
            spec words  sould not be here (for, if, func, match, return..)
        '''
        prels('CaseFunCall.match', elems)
        if len(elems) < 3:
            return False
        if elems[0].type != Lt.word:
            return False
        if not isLex(elems[1], Lt.oper, '('):
            return False
        # TODO: use word(any-with-brackets) pattern
        endInd = afterNameBr(elems)
        if endInd != -1:
            return False
        return True
        
        # if elems[1].type != Lt.oper or elems[-1].type != Lt.oper or elems[1].text != '(' or elems[-1].text != ')':
        #     return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' '''
        # 1. func name, in next phase: method call: inst.foo() ? separated case for objects with members: obj.field, obj.method()
        # 2. arg-expressions
        name = elems[0].text
        # argSrc = elems[2:-1]
        sub = elems[2:-1]
        cs = CaseCommas()
        subs = [sub] # one expression inside by default
        if cs.match(sub):
            _, subs = cs.split(sub)
        exp = FuncCallExpr(name)
        return exp, subs

    def setSub(self, base:FuncCallExpr, subs:Expression|list[Expression])->Expression: 
        ''' base - FuncCallExpr, subs - argVal expressions '''
        for exp in subs:
            base.addArgExpr(exp)
        return base

class CaseReturn(SubCase):
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'return'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' We have to 
        1. store result of next after return expr
        2. stop execution next lines'''
        subs = [elems[1:]]
        exp = ReturnExpr()
        return exp, subs
    
    def setSub(self, base:ReturnExpr, subs:list[Expression])->Expression:
        base.setSub(subs[0])
        return base


