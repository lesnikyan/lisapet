'''
'''


from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.utils import *
from cases.tcases import *
# from nodes.oper_nodes import *
# from nodes.func_opers import FuncApplyOper
from nodes.datanodes import *



class CaseListGen(SubCase, SolidCase):
    ''' Arithmetic sequence 
        [a .. b]
        [a, b .. c]
    '''
    
    def __init__(self):
        super().__init__()
        self.cs = CaseSeq('..')
        self.cc = CaseCommas()
    
    def match(self, elems:list[Elem]) -> bool:
        if not isLex(elems[-1], Lt.oper, ']'):
            return False
        return self.cs.match(elems[1:-1])

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[1:-1]
        subs = [sub]
        if self.cs.match(sub):
            _, subs = self.cs.split(sub)
        exp = ListGenExpr()
        return exp, subs

    def setSub(self, base:ListGenExpr, subs:Expression|list[Expression])->Expression:
        base.setArgs(*subs)
        return base


class CaseComprehension(SubCase, SolidCase):
    '''
    Basic class for comprehension expressions
    '''
    
    
    def __init__(self):
        super().__init__()
        self.spl = OperSplitter.getInst()
        self.cs = CaseSemic()
        self.splitInds = (1, -1)

    def getExpr(self) -> ComprehensionGen:
        return ListComprExpr()

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        sub = elems[self.splitInds[0]: self.splitInds[1]]
        _, subs = self.cs.split(sub)
        exp = self.getExpr()
        subs = [s for s in subs if len(s)]
        # prels('LC.elems = :', elems, show=1) 
        # prels('CompGen subs=', subs, show=1)
        return exp, subs

    def setSub(self, base:Block, subs:Expression|list[Expression])->Expression:
        # print('CaseComprehension.setSub: ', base, subs)
        base.setInner(subs)
        return base


class CaseListComprehension(CaseComprehension):
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
         
    def match(self, elems:list[Elem]) -> bool:
        
        if len(elems) < 7:
            return False
        if not (isLex(elems[0], Lt.oper, '[') and isLex(elems[-1], Lt.oper, ']') ):
            return False
        
        return self.cs.match(elems[1:-1])

    def getExpr(self) -> ComprehensionGen:
        return ListComprExpr()


class CaseDictComprehension(CaseComprehension):
    '''
    Comprehension generator for dict
    {k:v ; k, v <- src; x = k; x != v}
    '''
    
    def __init__(self):
        super().__init__()
        self.spl = OperSplitter.getInst()
        self.cs = CaseSemic()
    
         
    def match(self, elems:list[Elem]) -> bool:
        
        if len(elems) < 11:
            return False
        if not (isLex(elems[0], Lt.oper, '{') and isLex(elems[-1], Lt.oper, '}') ):
            return False
        
        return self.cs.match(elems[1:-1])

    def getExpr(self) -> ComprehensionGen:
        return DictComprExpr()


class CaseBytesComprehension(CaseComprehension):
    def __init__(self):
        super().__init__()
        self.splitInds = (2, -1)
    
    def match(self, elems:list[Elem], ind=-1) -> bool:
        if len(elems) < 7:
            return False
        if not isLex(elems[0], Lt.num, '0x'):
            return False
        if not isLex(elems[1], Lt.oper, '[') and not isLex(elems[-1], Lt.oper, ']'):
            return False
        # print('$1', len(elems), isLex(elems[0], Lt.num, '0x'), isLex(elems[1], Lt.oper, '['), isLex(elems[-1], Lt.oper, ']'))
        # print('$2', elemStr(elems[2:-1]))
        return self.cs.match(elems[2:-1])
    
    def getExpr(self) -> ComprehensionGen:
        return BytesComprExpr()


class CaseStringComprehension(CaseComprehension):
    def __init__(self):
        super().__init__()
        self.splitInds = (2, -1)
    
    def match(self, elems:list[Elem], ind=-1) -> bool:
        # print('$SGen:', elemStr(elems))
        if len(elems) < 6:
            return False
        if not isLex(elems[0], Lt.oper, '~'):
            return False
        if not isLex(elems[1], Lt.oper, '[') and not isLex(elems[-1], Lt.oper, ']'):
            return False
        return self.cs.match(elems[2:-1])

    def getExpr(self) -> ComprehensionGen:
        return StringComprExpr()


class CaseInlineGen(CaseComprehension):
    ''' (: n ; n <- nn ; expr...) '''
    def __init__(self):
        super().__init__()
        self.splitInds = (2, -1)
    
    def match(self, elems:list[Elem], ind=-1) -> bool:
        # print('$SGen:', elemStr(elems))
        if len(elems) < 6:
            return False
        if not isLex(elems[1], Lt.oper, ':'):
            return False
        if not isLex(elems[0], Lt.oper, '(') and not isLex(elems[-1], Lt.oper, ')'):
            return False
        return self.cs.match(elems[2:-1])

    def getExpr(self) -> InlineGenExpr:
        return InlineGenExpr()
