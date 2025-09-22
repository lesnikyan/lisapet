

import os

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.utils import *
from cases.tcases import ExpCase

from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.datanodes import *
from nodes.control import *
from nodes.func_expr import *

class CaseImport(ExpCase):
    ''' import module1
        import module1.sub1 # submodule
        import module1 > * # any from module
        import module1 mod1 # importing alias
        import module1 > foo # import function, type, const
        import module1 > foo f1 # import from module with alias
        import mod > foo1, foo2, foo3, CONST_1, AbcType # multiimport
        import mod > foo f1, bar f2, CONST1 C1 # multiimport with alias
    '''
    def match(self, elems:list[Elem])-> bool:
        if len(elems) < 2:
            return False
        if isLex(elems[0], Lt.word, 'import'):
            return True
    
    def expr(self, elems:list[Elem])-> tuple[Expression, Expression]:
        ''' return base expression, Sub(elems) '''
        # module = elems[0].text
        # prels('>>', elems, show=1)
        # lang.FullPrint = 0
        path, names = self.splitElems(elems[1:])
        # print('path, names::', path, names )
        expr = ImportExpr(path, names)
        return expr

    def splitElems(self, elems:list[Elem])->tuple:
        path = []
        # prels('ImportCase splitElems: ', elems)
        # imnames = []
        # inPath = True
        afterMore = False
        
        importList = [] # importing names (after >): foo, bar; ot: foo f1, bar f2
        # Path loop
        cnt = 0 # elem counter
        for ee in elems:
            cnt += 1
            if isLex(ee, Lt.oper, '>'):
                afterMore = True
                break
            if isLex(ee, Lt.oper, '.'):
                continue
            if 0 and  len(path) > 0 and isLex(ee, Lt.oper, '*'):
                path.append(ee.text)
                # importList.append('*')
                return path, importList
                # if * - end of correctPath
                # break
            if ee.type == Lt.word:
                path.append(ee.text)
            else:
                raise InterpretErr('Incorrect lexem in the import path')
        if len(elems) == cnt or not afterMore:
            return path, importList
        
        # if not afterMore:
        #     return 
        
        #  > name , name , name alias
        
        part = []
        remElems = elems[cnt:]
        # prels('Import Case splitElems2: ', remElems, show=1)
        
        if len(remElems) > 0 and isLex(remElems[0], Lt.oper, '*'):
            return path, ['*']
        
        for ee in remElems:
            if isLex(ee, Lt.oper, ','):
                # next name
                importList.append(part)
                part = []
                continue
            if ee.type == Lt.word:
                part.append(ee.text)
                continue
        if part:
            importList.append(part)
        return path, importList

    def fileByPath(self, path:list[str]):
        # print('fbp1:', path)
        pathElems = path[:-1]
        # dirPath = ''
        fname = '%s.%s' % (path[-1], CODE_EXT)
        pathElems.append(fname)
        # if len(dirs) > 0:
        #     dirPath = os.path.join(*dirs)
        # print('fbp::', pathElems)
        return os.path.join(*pathElems)
