'''

'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex


'''
oper group replacement:
`1` >=> ,
'''




def isHexBytes(elems:list[Elem]):
    rx = re.compile(r'[0-9a-f]+', flags=re.I)
    if len(elems) < 2:
        return False
    xtype = [Lt.word, Lt.num]
    for el in elems:
        if el.type not in xtype or not rx.match(el.text):
            return False
    return True

operPrior = ('( ) [ ] { } , . , ~> , ... , -x ! ~ , ** , * / % , + - ,'
' << >> , =~ ?~ /~, < <= > >= !> ?> !?>, == != , &, ^ , | , ::, && , || , \\ , ->, $, ?: , : , ?, `1`, .. , <- , = += -= *= /= %= , ; , !: :? => , /: ')

unaryOperators = '- ! ~'.split(' ')

SPEC_WORDS = 'for while if else func type def struct var match case'.split(' ')


def getOperPriors():
    return [raw.replace('`1`', ',') for raw in operPrior.split(',')]


def isGetValExpr(elems:list[Elem]):
    ''' If solid  expressions 
    of var, func call, obj member, collection elem, etc '''

    inBr = 0
    obr = [s for s in '([{']
    cbr = [s for s in ')]}']
    lem = len(elems)
    
    if lem < 1 :
        return False
    varOpers = '([{}]).'
    for i in range(0, lem):
        ee = elems[i]
        
        # close br
        if isLex(ee, Lt.oper, cbr):
            inBr -= 1
        
        #open br
        if isLex(ee, Lt.oper, obr):
            inBr += 1
        
        if inBr > 0:
            continue
        
        # not in br
        if ee.type == Lt.word or (ee.type == Lt.oper and ee.text in varOpers):
            # just valid var, or func call, or collectio[elem], or obj.field 
            continue
        # print('utils.geVar4: ', ee.text, ' __ ', inBr)
        # any other lexem means that whole expression not what we expect
        return False
    return True

def isBrPair(elems:list[Elem], opn, cls):
    return isLex(elems[0], Lt.oper, opn) and isLex(elems[-1], Lt.oper, cls)

def el_text(elems:list[Elem]):
    return [n.text for n in elems]

def prels(pref, elems:list[Elem], *args, **kwargs):
    ''' Print list of elems '''
    if not (FullPrint or ('show' in kwargs and kwargs['show'])):
        return
    if not elems:
        # print(pref, '-empty-')
        return
    
    # list[list[Elem]]
    if isinstance(elems[0], (list, tuple)):
        # print(pref, end='')
        for subel in elems:
            print(el_text(subel), end=' $$ ', sep = ' ')
        print('')
        return

    # list[Elem]
    print(pref, el_text(elems), *args)


def elemStr(elems:list[Elem], delim=' '):
    # dprint('debug elemStr', elems)
    return delim.join([ee.text for ee in elems])

class OperSplitter:
    def __init__(self, priors=None):
        priorSrc = operPrior
        self.defPrior = True
        if priors:
            priorSrc = priors
            self.defPrior = False
        # print('utils.OperSplitter:', priorSrc)
        priorGroups = [raw.replace('`1`', ',') for raw in priorSrc.split(',')]
        self.priorGroups = [[ n for n in g.split(' ') if n.strip()] for g in priorGroups]
        self.opers = [oper for nn in self.priorGroups[:] for oper in nn]


    def mainOper(self, elems:list[Elem])-> int:
        '''
        Find the main operator in the string.
        First operator with lowest priority from the end will be returned.
        e.g. + or - for math expressions with + - / *
        or || for logical expressions. 
        '''
        
        # print('OperSplitter #a51:', [n.text for n in elems])
        # src = elemStr(elems)
        lowesPrior = len(self.priorGroups) - 1
        obr='([{'
        cbr = ')]}'
        leftOfRarr = False # [\] word [, word]
        backAssoc = ['/:']
        unarIndex = -111
        if self.defPrior:
            unarIndex = [gi for gi in range(len(self.priorGroups)) if '-x' in self.priorGroups[gi]].pop()
        # print('u-unar', unarIndex, self.priorGroups[unarIndex])
        # print('~- OperSplitter', len(elems))
        # prels('~~ OperSplitter', elems, show=1)
        if len(elems) < 2:
            return -1
        lem = len(elems)
        if lem == 0:
            return -1 # empty input
        for prior in range(lowesPrior, -1, -1):
            curPos = lem
            obr='([{'
            cbr = ')]}'
            # if len(self.priorGroups) < 500:
            #     print('prior=', prior, self.priorGroups[prior] )
            step = -1
            elIter = range(lem - 1, -1, -1)
            if self.priorGroups[prior][0] in backAssoc:
                # means that all opers in group have the same direction of assoc
                # print('OperSplitter. back-assoc', self.priorGroups[prior])
                step = 1
                curPos = -1
                elIter = range(0, lem)
                cbr='([{'
                obr = ')]}'
            inBrs = [] # brackets which was opened from behind
            # print('$prior: ', self.priorGroups[prior])
            leftOfRarr = False
            # lamLef = []
            for i in elIter:
                curPos += step
                if curPos < 0 : # or curPos >= lem
                    return curPos # Nothing was found
                el = elems[i]
                etx = el.text
                # if self.priorGroups[prior][0] in backAssoc:
                #     print('spl1:', i, el.text, Lt.name(el.type), (el.text in self.priorGroups[prior]), ' pos =', curPos, inBrs)
                
                # counting brackets from tne end, closed is first
                # dprint('ue:', i, ':', etx, '>>', '`'.join(inBrs))
                if etx and etx in cbr:
                    inBrs.append(etx)
                    # print('inbr append: ', '>>', inBrs)
                    continue
                if etx and etx in obr:
                    if len(inBrs):
                        last = inBrs.pop()
                        # print('inbr pop: ',last, '>>', inBrs)
                    # dprint(' << ', etx, last)
                    if i == 0 and etx in self.priorGroups[prior]:
                        # print('end of prior / open', obr)
                        return 0
                    continue
                # print('@#', etx, 'br:', inBrs)
                    # TODO: check equality of brackets pairs (not actual for valid code, because [(]) is invalid )
                if len(inBrs) > 0:
                    continue
                # if self.priorGroups[prior][0] in backAssoc:
                    # print('>>>>>>>> DEBUG 1')
                if el.type != Lt.oper:
                    continue
                if el.text not in self.opers:
                    continue

                if leftOfRarr:
                    if el.text != ',' and i > 0:
                        leftOfRarr = False
                    else:
                        continue
                if el.text == '->':
                    leftOfRarr = True

                if el.text in ['-', '+', '!', '~']:
                    if i > 0 and elems[i-1].type == Lt.oper and elems[i-1].text not in ')]}':
                        # unary case found, skip current pos
                        # print(' >> == unary case found:', i, el.text)
                        continue
                    if i == 0 and prior != unarIndex:
                        # print(' >> == unary case in 0:', i, el.text)
                        continue
                if el.text in self.priorGroups[prior]:
                    # we found current split item
                    # print('oper-found> [%d ? %d]' % (i, curPos), '`%s`' % src, elemStr(elems[0:i]), '<(%s)>' % elems[i].text, elemStr(elems[i+1:]))

                    return curPos # The main Result
        if isLex(elems[0], Lt.oper, unaryOperators):
            # dprint('oper-found> unary [0 : %s]' % elems[0].text ) 
            return 0
        return -1 # debug output, won't happened in real case



def flatOpers():
    opers = getOperPriors()[4:]
    fopers = []
    for oops in opers:
        # print(oops.split(' '))
        fopers.extend([n for n in oops.split(' ') if n and  n not in ' .'])
    return fopers

_noSolidOpers = flatOpers()

_keyWords = (
    'if else while for match func struct import @debug'
).split(' ')

def isSolidExpr(elems:list[Elem], getLast=None):
    ''' single varName or chain of fields, subelem, call 
    
        getLast - get pos of lastsubpart like word after dot, brackets
    '''
    # print('isSolid #1', elemStr(elems))
    elen = len(elems)
    if elen == 0:
        return False
    
    if elen == 1 and elems[0].type in [Lt.word, Lt.text, Lt.num]:
        return True
    
    # print('isSolid #2', f"<{elems[0].text}>", elems[0].text in _keyWords)
    if elems[0].type == Lt.word and elems[0].text in _keyWords:
        return False
    
    if isHexBytes(elems):
        return False

    fopers = _noSolidOpers
    # print('solid-fopers', fopers)
    opened = [] # brackets openede from right
    # cbr = []
    rob = list('}])')
    rcb = list('([{')
    bpairs = {'(':')', '[':']', '{':'}'}
    # print('ss:', end=' ')
    for i in range(elen-1, -1, -1):
        el = elems[i]
        etx = el.text
        # print('=>', '', etx, end=' ')
        et = el.type
        if isLex(el, Lt.oper, rob):
            # open brackets from right
            opened.append(el.text)
            continue
        if isLex(el, Lt.oper, rcb):
            # close brackets
            if len(opened) == 0:
                # posibly multiline expr
                # print('No-solid?', len(opened))
                return False
            lastObr = opened.pop()
            if bpairs[etx] != lastObr:
                # incorrect brackets pair in closing
                raise InterpretErr(f"incorrect brackets pair in closing `{etx}{bpairs[etx]}`")
                # return False
            if len(opened) == 0 and getLast:
                # last closed part found in solidExpr
                return True, i
            continue
        if not opened and isLex(el, Lt.oper, fopers):
            # any operator has been found not in brackets a + b, excepr [. ~>]
            # print('back-i:%d'%i, 'No Solid because of ', etx)
            return False
    # print('\n>> ', opened, ' //')
    return not opened

def isFuncCall(elems:list[Elem]):
    ''' solid expr with func call in the end
        a()
        a(args)
        a.b()
        a[0]()
        a()()
        a.b()()
    '''

def isField(elems:list[Elem]):
    ''' solid expr with `.fieldName` in the end 
        a.b
        a().b
        a.b().c
        a.b[0].c
    '''
    if not isLex(elems[-2], Lt.oper, '.'):
        return False
    
    return elems[-1].type == Lt.word and elems[-1].text

def isSeqElem(elems:list[Elem]):
    ''' solid expr with square brackets in the end
        a[0]
        a.b[0]
        a()[0]
        
    '''
