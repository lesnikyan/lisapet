'''

'''


from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex


'''
oper group replacement:
`1` >=> ,
'''

operPrior = ('( ) [ ] { } , . , -x !x ~x , ** , * / % , + - ,'
' << >> , < <= > >= !> ?> !?>, == != , &, ^ , | , && , ||, ?: , : , ? , `1`, <- , ->, = += -= *= /= %= , ; , /: !: , !- ')

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
    # not [...], (...), {,,,}, "qwerty", +- * % ! < > / && |
    # if lem < 1 or elems[0].type != Lt.word or isLex(elems[0], Lt.oper, obr):
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
    if not (FullPrint or ('show' in kwargs and kwargs['show'])):
        return
    
    # list[list[Elem]]
    if isinstance(elems[0], (list, tuple)):
        print(pref, end='')
        for subel in elems:
            print(el_text(subel), end=' $$ ', sep = ' ')
        print('')
        return

    # list[Elem]
    print(pref, el_text(elems), *args)


def elemStr(elems:list[Elem]):
    # dprint('debug elemStr', elems)
    return ' '.join([ee.text for ee in elems])

class OperSplitter:
    def __init__(self, priors=None):
        priorSrc = operPrior
        if priors:
            priorSrc = priors
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
        src = elemStr(elems)
        lowesPrior = len(self.priorGroups) - 1
        obr='([{'
        cbr = ')]}'
        backAssoc = ['/:']
        inBrs = [] # brackets which was opened from behind
        # prels('~~ OperSplitter', elems)
        lem = len(elems)
        if lem == 0:
            return -1 # empty input
        for prior in range(lowesPrior, -1, -1):
            curPos = lem
            obr='([{'
            cbr = ')]}'
            # if len(self.priorGroups) < 5:
            #     print('prior=', prior, self.priorGroups[prior] )
            step = -1
            eliter = range(lem - 1, -1, -1)
            if self.priorGroups[prior][0] in backAssoc:
                # means that all opers in group have the same direction of assoc
                # print('OperSplitter. back-assoc', self.priorGroups[prior])
                step = 1
                curPos = -1
                eliter = range(0, lem)
                cbr='([{'
                obr = ')]}'
            
            # for i in range(lem - 1, -1, -1):
            for i in eliter:
                curPos += step
                if curPos < 0 : # or curPos >= lem
                    return curPos # Nothing was found
                el = elems[i]
                etx = el.text
                # if self.priorGroups[prior][0] in backAssoc:
                #     print('spl1:', i, el.text, Lt.name(el.type), (el.text in self.priorGroups[prior]), ' pos =', curPos, inBrs)
                
                # counting brackets from tne end, closed is first
                # dprint('ue:', i, ':', etx, '>>', '`'.join(inBrs))
                if etx in cbr:
                    inBrs.append(etx)
                    continue
                if etx in obr:
                    if len(inBrs):
                        last = inBrs.pop()
                    # dprint(' << ', etx, last)
                    # if len(inBrs) == 0 and etx in self.priorGroups[prior]:
                    #     return i
                    if i == 0 and etx in self.priorGroups[prior]:
                        return 0
                    continue
                    # TODO: check equality of brackets pairs (not actual for valid code, because [(]) is invalid )
                if len(inBrs) > 0:
                    continue
                # if self.priorGroups[prior][0] in backAssoc:
                    # print('>>>>>>>> DEBUG 1')
                if el.type != Lt.oper:
                    continue
                if el.text not in self.opers:
                    continue
                if i > 0 and el.text in ['-', '+', '!', '~'] and elems[i-1].type == Lt.oper and elems[i-1].text not in ')]}':
                    # unary case found, skip current pos
                    # dprint(' >> == unary case found:', i, el.text)
                    continue
                if el.text in self.priorGroups[prior]:
                    # we found current split item
                    dprint('oper-found> [%d ? %d]' % (i, curPos), '`%s`' % src, elemStr(elems[0:i]), '<(%s)>' % elems[i].text, elemStr(elems[i+1:]))

                    return curPos # The main Result
        if isLex(elems[0], Lt.oper, unaryOperators):
            dprint('oper-found> unary [0 : %s]' % elems[0].text ) 
            return 0
        return -1 # debug output, won't happened in real case



