

from vars import *
from nodes.expression import *

from libs.regexp import compile, str2flags


class ReturnExpr(Expression):
    ''' '''
    def __init__(self):
        super().__init__()
        self.sub:Expression = None
        # self.val = None
        

    def setSub(self, exp:Expression):
        ''' sub expr '''
        self.sub = exp

    def do(self, ctx:Context):
        ''' eval sub'''
        self.sub.do(ctx)
        self.val = FuncRes(self.sub.get())

    def get(self) -> Var|list[Var]:
        return self.val


class BreakExpr(Expression):
    ''' '''
    def __init__(self):
        super().__init__(None, 'break')
        # self.sub:Expression = None

    # def setSub(self, exp:Expression):
    #     ''' sub expr '''
    #     self.sub = exp

    def do(self, ctx:Context):
        ''' eval sub'''
        # self.sub.do(ctx)
        self.val = PopupBreak()

    def get(self) -> Var|list[Var]:
        return self.val


class ContinueExpr(Expression):
    ''' '''
    def __init__(self):
        super().__init__(None, 'continue')
        # self.sub:Expression = None
        

    # def setSub(self, exp:Expression):
    #     ''' sub expr '''
    #     self.sub = exp

    def do(self, ctx:Context):
        ''' eval sub'''
        # self.sub.do(ctx)
        self.val = PopupContinue()

    def get(self) -> Var|list[Var]:
        return self.val


class RegexpExpr(Expression):
    
    def __init__(self, patt, flags, src):
        super().__init__(None, src)
        # print('RegexpExpr:', patt, flags)
        self.pattern = patt
        self.flags:str|Expression = flags
        self.rule = None

    def do(self, ctx:Context):
        flags = self.flags
        if isinstance(flags, Expression):
            flags.do(ctx)
            flags = var2val(flags.get()).getVal()
        numFlags = str2flags(flags)
        rule = compile(self.pattern, numFlags)
        self.rule = Regexp(rule)


    def get(self) -> Regexp:
        return self.rule
