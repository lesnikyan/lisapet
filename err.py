'''
Handling parsing and runtypme errors.

'''


from lang import *
from base import *
from nodes.expression import *


class ParseErrHandler:
    
    def __init__(self):
        pass


class RunErrHandler:
    
    def __init__(self):
        pass
    
    def errMsg(self, exc:Exception, expr:Expression):
        print('Error:', exc, exc.args)
        print(f'In line: {expr.src.line}: {expr.src.src}')

    def interp(self, exc:LangError, src:CLine):
        print('Interpretation error:', exc, exc.masg)
        print(f'In line: {src.line}: {src.src}')

    def handle(self, expr:Expression, ctx:Context):
        try:
            expr.do(ctx)
        except ParseErr as exc:
            self.errMsg(exc, expr)
        except InterpretErr as exc:
            self.errMsg(exc, expr)
        except EvalErr as exc:
            self.errMsg(exc, expr)
        except TypeErr as exc:
            self.errMsg(exc, expr)
        except LangError as exc:
            self.errMsg(exc, expr)
        except Exception as exc:
            self.errMsg(exc, expr)
