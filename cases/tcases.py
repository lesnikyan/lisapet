'''
ExpCases here for exec tree
'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.datanodes import *
from nodes.control import *
from nodes.func_expr import *


SPEC_WORDS = 'for while if else func type def struct var match case'.split(' ')
EXT_ASSIGN_OPERS = '+= -= *= /= %='.split(' ')


def elemStr(elems):
    return ' '.join([ee.text for ee in elems])

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
        # print(ee.text)
        if inBr:
            # if ee.text == ']':
            # print('in BR. continue', ee.text, ee.text in ')]')
            if ee.text in ')]':
                # close brackets
                inBr -= 1
                continue
        # print('inbr ', inBr)
        # if ee.type == Lt.oper and  ee.text == '[':
        if ee.type == Lt.oper and  ee.text in '([':
            # enter into brackets
            inBr += 1
            continue
        if inBr:
            continue
        # print('@@ after', i, elems[i].text)
        if i > 0 and ee.type != Lt.word and (ee.type == Lt.oper and ee.text not in '.,:'):
            # print('break:<(', ee.text,')> >> ',  elemStr(elems[:i+1]))
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
                # print('# ee:', ee.text, 'inbr:', inBr)
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
        # if inBr:
        if ee.text in cbr :
            # print('#close', ee.text)
            if obr.index(inBr[-1]) != cbr.index(ee.text):
                # print('# ee:', ee.text, 'inbr:', inBr)
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


def isBrPair(elems:list[Elem], opn, cls):
    return isLex(elems[0], Lt.oper, opn) and isLex(elems[-1], Lt.oper, cls)


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
        s = ''.join([n.text for n in elems])
        if elems[0].type == Lt.comm:
            # print('CaseComment.match', s)
            return True
        return False

    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        CommentExpr(''.join([n.text for n in elems]).lstrip())


class CaseVal(ExpCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) > 1:
            return False
        if elems[0].type in [Lt.num, Lt.text]:
            return True
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


class BlockCase(ExpCase):
    ''' control sub and inner sub 
        function, for-loop, if-statement, match-case statement
    '''


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
                res.append(sub)
                continue
        # print('Seq.split, start =', start, 'len-elems =', len(elems))
        if start < len(elems):
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


class CaseDot(CaseSeq):
    ''' key.val  '''
    def __init__(self):
        super().__init__('.')


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
        src = elemStr(elems)
        name = elems[0].text
        # argSrc = elems[2:-1]
        sub = elems[2:-1]
        cs = CaseCommas()
        subs = [sub] # one expression inside by default
        if cs.match(sub):
            _, subs = cs.split(sub)
        exp = FuncCallExpr(name, src)
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


