import io
import code
from contextlib import redirect_stdout, redirect_stderr

# from importlib import import_module
# from .restricted import safe_globals

# safe_modules = {
#     'math', 'random', 'time', 'datetime', 'json', 're', 
#     'itertools', 'functools', 'operator', 'collections', 
#     'heapq', 'bisect', 'array', 'queue', 'contextlib', 'dataclasses',
#     'typing', 'abc', 'enum', 'copy', 'requests', 'numbers', 'pprint', 
#     'numpy', 'scipy', 'pandas', 'matplotlib', 'sklearn'
# }

# def safe_import(name, *args, **kwargs):
#     if name in safe_modules:
#         return import_module(name)
#     else:
#         raise ImportError(f'import {name} is not allowed')

# safe_globals.update(
#     print=print, __import__=safe_import, vars=vars,
#     min=min, max=max, dict=dict, list=list, iter=iter,
#     sum=sum, all=all, any=any, map=map, filter=filter,
#     enumerate=enumerate, getattr=getattr, 
# )


class Console(code.InteractiveConsole):

    def __init__(self, namespace=None) -> None:
        super().__init__(namespace)
        # self.locals = safe_globals
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()

    def write(self, data: str) -> None:
        self.stderr.write(data)
        
    def push(self, line: str) -> bool:
        with redirect_stdout(self.stdout), redirect_stderr(self.stderr):
            return super().push(line)

    def run(self, code: str) -> dict[str, str]:
        if not code.strip():
            return dict(stdout='', stderr='')

        incomplete = False
        for line in code.splitlines() + ['']:
            if incomplete and not line.startswith(tuple(' \t#')):
                self.push('')
            incomplete = self.push(line)
        if incomplete:
            self.write("SyntaxError: incomplete input")
            self.resetbuffer()

        res = dict(stdout=self.stdout.getvalue(), stderr=self.stderr.getvalue())
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        return res


if __name__ == "__main__":
    console = Console()
