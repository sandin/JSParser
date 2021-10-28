import unittest

from ..jsparser import parser
from ..jsparser import codegen


class ParserTest(unittest.TestCase):

    def test_parse_code_to_ast(self):
        js_code = """
            function add(arg0, arg1) {
                return arg0 + arg1;
            }
        """
        ctx = {"globals": [], "functions": []}
        parser.parse_code_to_ast(js_code, ctx)
        self.assertEqual(1, len(ctx['functions']))
        self.assertEqual("add", ctx['functions'][0].proto.name)

        py_code = codegen.generate_python_code(ctx)
        g = {}
        exec(py_code, g)
        self.assertTrue("add" in g)
        self.assertEqual(3, g['add'](1, 2))  # invoke: add(1, 2) = 3


if __name__ == '__main__':
    unittest.main()
