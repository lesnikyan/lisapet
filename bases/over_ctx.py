'''
Docstring for nodes.over_ctx
'''

# from vars import *
from base import VType, EvalErr
from typex import FuncInst

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
        # print('FOver.add', self.name, count, self.overs)
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

    
    def get(self, argSet=list):
        '''
        :param argSet: like [int, float, string]
        '''
        count = len(argSet)
        # print('44#>>', count, count in self.overs, self.overs.keys())
        if count in self.overs:
            byCount = self.overs[count]
            if isinstance(byCount, FuncInst):
                return byCount
            # next - search by types
            if not isinstance(self.overs[count], dict):
                # some strange
                return None
            # print(self.overs[count].keys())
            fhash = FuncInst.sigHash(argSet)
            if fhash in self.overs[count]:
                return self.overs[count][fhash]
            # search by type compatibility
        
        return None

