
from . import parser
from . import codegen


class JSEngine(object):

    def __init__(self, g = {}):
        self._g = g
        externals = {
            "Math.max": "max",
            "Math.min": "min",
        }
        self._ctx = {"globals": [], "functions": [], "externals": externals}

    def eval(self, js_code):
        parser.parse_code_to_ast(js_code, self._ctx)
        py_code = codegen.generate_python_code(self._ctx)
        exec(py_code, self._g)

    def set(self, key, val):
        self._g[key] = val

    def set_all(self, values):
        self._g = { **self._g, **values }

    def get(self, key):
        return self._g[key] if key in self._g else None
