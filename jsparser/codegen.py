
def generate_python_code(ctx):
    code = ""
    for g in ctx['globals']:
        code += str(g.body) + "\n"

    code += "\n"
    for function_ast in ctx['functions']:
        code += str(function_ast)
    return code
