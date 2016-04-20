from __future__ import print_function
import inspect,os
try:
    import __builtin__ as builtins # Python 2
except ImportError:
    import builtins # Python 3

# http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern
class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated
    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance
    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')
    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class printerer:
    def nullprefix(self):
        frame,filename,line_number,function_name,lines,index = inspect.stack()[3] #http://stackoverflow.com/a/22378386 - loosely
        return "[%s:%s@%d] " % (os.path.basename(filename), function_name, line_number)
    def __init__(self):
        self.prefixer = self.nullprefix
    def setPrefixer(self, p=None):
        if p == None:
            self.prefixer = self.nullprefix
        else:
            self.prefixer = p
    def prefix(self):
        return self.prefixer()
global _print
_print = print # keep a local copy of the original print
builtins.print = lambda *args, **kwargs: _print(printerer.Instance().prefix(), *args, **kwargs)

def realprint(*args, **kwargs):
    _print(*args, **kwargs)
