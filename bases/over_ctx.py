'''
Docstring for nodes.over_ctx
'''

# from vars import *
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
            # 1 added before
            self.overs[count] = func
    
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
        
        return None

