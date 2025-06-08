
"""
Structural components of execution tree.
"""

from lang import *
from vars import *
from nodes.expression import *
from context import Context, ModuleContext

# Expression




class Module(Block, ModuleTree):
    ''' Level of one file. 
    functions, constants, structs with methods '''
    def __init__(self, name='default'):
        super().__init__()
        self.context:ModuleContext = None
        self.name = name
        self.imported:dict[str, Context] = {}

    def getName(self):
        return self.name

    # def setContext(self, ctx:Context):
    #     self.context = ctx

    def do(self, ctx:Context):
        if (ctx):
            self.context = ctx
        super().do(self.context)

    # def get(self, name=None):
    #     # DEBUG output
    #     if name is None:
    #         return f'@module({self.name})'
    #     # get thing from context
    #     thing = self.context.get(name)
    #     if thing:
    #         return thing
    #     return None

    # def importIn(self, name, module):
    #     ''' Add other modules here'''
    #     self.imported[name] = module
    #     # TODO: merge contexts by resolved names
        
    # def exportOut(self):
    #     ''' Call from other module `importIn '''
    #     return self.ctx


class ImportExpr(Expression):
    
    ''' import module1
        import module1.sub1 # submodule
        import module1.* # any from module
        import module1 mod1 # importing alias
        import module1 > foo # import function, type, const
        import module1 > foo f1 # import from module with alias
        import mod > foo1, foo2, foo3, CONST_1, AbcType # multiimport
        import mod > foo f1, bar f2, CONST1 C1 # multiimport with alias

        Imported module is added to currend module context.impoted
        If only list from molule import(mod > list): listed things is added into cur context: funcs, structs, Vars
    '''
    
    def __init__(self, path, elems:list[list[str]], src = ''):
        super().__init__(None, src)
        self.fullImport = False
        # print('ImportExpr __init:', elems)
        if (len(path) > 1 and path[-1] == '*' and len(elems) == 0):
            self.fullImport = True
            path = path[:-1]
        self.modName = path[-1] # final name of imported module
        self.modPath = path # if more than 1 name, path will be a list
        self.names = {}
        if not self.fullImport and len(elems):
            self.parseElems(elems)

    def parseElems(self, elems:list[list[str]]):
        '''
        elems: [ ['name'], ['name', 'alias'] ]
        '''
        print('ImportExpr.parseElems')
        if len(elems) == 0:
            return
        for elm in elems:
            print('$elm:', elm)
            match len(elm):
                case 1: self.names[elm[0]] = elm[0]
                case 2: self.names[elm[0]] = elm[1]
                case _: raise InterpretErr('Too many words in importing element: [%s]' % ','.join(elm))
    
    def do(self, ctx:ModuleContext):
        '''  '''
        # 1. find module by path
        mdl:Module = ctx.findloaded(self.modName) # module eval-tree
        print('import.do, mod:', mdl)
        # 2. add module or things to the module-context
        if mdl is None:
            raise EvalErr('Trying ro import module that hasn`t been loaded.')
        mctx = ModuleContext()
        mdl.do(mctx)
        module = ModuleBox(self.modName, mctx)
        aliases = {}
        if self.fullImport:
            module.importAll()
        elif len(self.names) > 0:
            for nm, alias in self.names.items():
                # print('import nm >>>>', nm, alias)
                if nm != alias:
                    aliases[alias] = nm
                module.importThing(nm)
        # raise EvalErr('')
        ctx.addModule(self.modName, module)
        # 2.1 Add aliases
        for alias, orig in aliases.items():
            ctx.addAlias(alias, orig)


