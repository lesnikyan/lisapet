
'''
Eval parsed lexems
'''



def f1(func, a):
    def ff():
        func(a)
    return ff

def f2(func, a):
    def ff(b):
        return func(a, b)
    return ff

    
