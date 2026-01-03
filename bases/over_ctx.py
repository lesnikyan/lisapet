'''
Docstring for nodes.over_ctx
'''

# from vars import *
from base import VType, EvalErr
from typex import FuncInst
from bases.ntype import checkCompatArgs

'''
# by arg count
self.overs = {
    0: foo()
    2: foo(a, b)
    3: foo(a,b,c)
}
# then by arg types
self.overs = {
    1:{
        int: foo(int)
        float: foo(float)
    },
    2: {
        int_float: foo(int, float),
        string_int: foo(string, int)
    }
}
'''
class FuncOverSet:
    def __init__(self, name):
        # print('F-Over--Init', name)
        self.name = name
        self.overs = {}

    def add(self, func:FuncInst):
        # put by count
        count = func.argCount()
        # print('\nFOver.add1', self.name, count, self.overs)
        # print('FOver.add2', self.name, [at.name for at in func.argTypes()])
        if count not in self.overs:
            # such count wasn't added before
            self.overs[count] = func
            return
        else: 
            argTypes:list[VType] = func.argTypes()
            fhash = FuncInst.sigHash(argTypes)
            
            if isinstance(self.overs[count], FuncInst):
                # second case with same arg count, add deeper dict by types
                prev:FuncInst = self.overs[count]
                self.overs[count] = {}
                prevHash = FuncInst.sigHash(prev.argTypes())
                self.overs[count][prevHash] = prev
                self.overs[count][fhash] = func
                return
            elif isinstance(self.overs[count], dict):
                if fhash in self.overs[count]:
                    # such func(types) already exists
                    raise EvalErr("Such function `{func.name}` with sigHash {fhash} already exists")
                self.overs[count][fhash] = func

    
    def get(self, argSet=list[VType]):
        '''
        :param argSet: like [int, float, string]
        '''
        count = len(argSet)
        # print('44#>>', count, count in self.overs, self.overs.keys())
        if count not in self.overs:
            return None
        func = self.overs[count]
        if isinstance(func, FuncInst):
            return func
        
        # next - strict search by types
        section:dict = func
        if not isinstance(section, dict):
            # some strange in current place
            return None
        # print('FOvers.get keys:', section.keys())
        fhash = FuncInst.sigHash(argSet)
        if fhash in section:
            return section[fhash]
        
        # search by type compatibility
        found = []
        for _, nfunc in section.items():
            ttypes = nfunc.argTypes()
            # print('FOvers.get nf  types:', ttypes)
            if checkCompatArgs(ttypes, argSet):
                found.append(nfunc)
        fc = len(found)
        if fc == 1:
            return found[0]
        if fc > 1:
            raise EvalErr(
                f'More than 1 compatible case found for overload function {self.name} '
                f'for call ({','.join([n.name for n in argSet])})')
        return None
        

