import unittest

from ..jsparser.engine import JSEngine


class EngineTest(unittest.TestCase):

    def test_eval(self):
        # create javascript runtime
        js_runtime = JSEngine()

        # bind global variables
        js_runtime.set("bar", 20)

        # eval javascript code
        js_runtime.eval("""
        var foo = 1.0;

        function get_bar() {
            return bar;   // variable defined in python
        }

        function add(a, b) {
            return a + b;
        }
        """)

        # invoke function defined in javascript
        add_func = js_runtime.get("add");
        result = add_func(1, 2)
        print("result:", result)
        # output: result: 3

        # get variable defined in javascript
        foo = js_runtime.get("foo")
        print("foo:", foo, "type:", type(foo))
        # output: foo: 1.0 type: int

        self.assertEqual(3, result)
        self.assertEqual(1.0, foo)


if __name__ == '__main__':
    unittest.main()
