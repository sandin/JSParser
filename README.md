# JSParser

Javascript Parser.


## Install

```bash
$ pip install -e .
```

## Usage

Convert Javascript code into python code.

```bash
$ jsparser input.js output.py
```

or

```bash
$ python -m jsparser.cli input.js output.py
```

## API

use Javascript runtime in python:
```python
from jsparser.engine import JSEngine


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
add_func(1, 2)

 # get variable defined in javascript
foo = js_runtime.get("foo")
print("foo:", foo, "type:", type(foo))
# output: foo: 1.0 type: int

```
