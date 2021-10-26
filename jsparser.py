from typing import Optional
import enum

# Lexer

g_last_char: str = ' '
g_identifier_str: str = None
g_number_val: float = 0
g_cur_token = None


class Token(enum.IntEnum):
    EOF = -1
    IDENTIFIER = -2
    NUMBER = -3
    NEW_LINE = -4
    # keywords:
    FUNCTION = -5
    RETURN = -6
    VAR = -7
    IF = -8
    THEN = -9
    ELSE = -10


g_keywords = {
    "function": Token.FUNCTION,
    "return": Token.RETURN,
    "var": Token.VAR,
    "if": Token.IF,
    "else": Token.ELSE
}


class StringBuffer(object):

    def __init__(self, value):
        self._value = value
        self._index = 0
        self._length = len(value)

    def getchar(self, peek = False):
        if self._index < self._length:
            c = self._value[self._index]
            if not peek:
                self._index += 1
            return c
        return None # EOF

    def eof(self):
        return self._index == self._length - 1

    def curline(self):
        start_index = self._index
        c = self._value[start_index]
        while c != "\r" and c != "\n" and start_index > 0:
            c = self._value[start_index]
            start_index -= 1
        if start_index > 0:
            start_index += 1 # skip the nl
        end_index = self._index
        c = self._value[end_index]
        while c != "\r" and c != "\n" and end_index < self._length:
            c = self._value[end_index]
            end_index += 1
        return self._value[start_index:end_index]


def get_token(code: StringBuffer):
    global g_last_char, g_identifier_str, g_number_val

    # skip the whitespace
    while g_last_char and g_last_char.isspace():
        g_last_char = code.getchar()

    if g_last_char is None: # EOF
        return Token.EOF

    if g_last_char.isalpha() or g_last_char == "_": # identifier: [a-zA-Z][a-zA-Z0-9]*
        g_identifier_str = g_last_char
        g_last_char = code.getchar()
        while g_last_char.isalnum() or g_last_char == "_":
            g_identifier_str += g_last_char
            g_last_char = code.getchar()
        if g_identifier_str in g_keywords:
            return g_keywords[g_identifier_str]
        return Token.IDENTIFIER

    if g_last_char.isdigit(): # Number: [0-9.]
        num_str = g_last_char
        g_last_char = code.getchar()
        while g_last_char.isdigit() or g_last_char == ".":
            num_str += g_last_char
            g_last_char = code.getchar()
        g_number_val = float(num_str)
        return Token.NUMBER

    if g_last_char == "/":
        next_char = code.getchar(peek=True)
        if next_char == "/": # // comment util end of line
            code.getchar() # eat '//'
            g_last_char = code.getchar()
            while g_last_char != None and g_last_char != "\n" and g_last_char != "\r":
                g_last_char = code.getchar()

            if g_last_char != None:
                return get_token(code)

    if g_last_char == "\r" or g_last_char == "\n" or g_last_char == ";":
        g_last_char = code.getchar() # eat nl
        while g_last_char == "\r" or g_last_char == "\n" or g_last_char == ";":
            g_last_char = code.getchar()
        return Token.NEW_LINE

    this_char = g_last_char
    g_last_char = code.getchar()
    return this_char


def get_next_token(code: StringBuffer):
    global g_cur_token
    g_cur_token = get_token(code)
    print("get_next_token, token=%s, str=%s, str_buffer=%s, num_buffer=%d" % (g_cur_token, g_last_char, g_identifier_str, g_number_val))
    return g_cur_token


# AST


class ExprAST(object):
    pass


class NumberExprAST(ExprAST):
    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return "%sf" % (self.value,)


class VariableExprAST(ExprAST):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "%s" % (self.name,)


class BinaryExprAST(ExprAST):
    def __init__(self, lhs: ExprAST, op: str, rhs: ExprAST):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def __str__(self):
        if self.op != "=":  # TODO: remove unnecessary paren
            return "(%s %s %s)" % (str(self.lhs), self.op, str(self.rhs))
        else:
            return "%s %s %s" % (str(self.lhs), self.op, str(self.rhs))


class VariableDeclarationExprAST(BinaryExprAST):
    def __init__(self, variable_expr: VariableExprAST, rhs: ExprAST):
        BinaryExprAST.__init__(self, variable_expr, "=", rhs)


class ReturnExprAST(ExprAST):
    def __init__(self, rhs: ExprAST):
        self.rhs = rhs

    def __str__(self):
        return "return %s" % (str(self.rhs),)


class CallExprAST(ExprAST):
    def __init__(self, callee: str, args: list):
        self.callee = callee
        self.args = args

    def __str__(self):
        args_str = ""
        for index, arg in enumerate(self.args):
            args_str += str(arg)
            if index < len(self.args) - 1:
                args_str += ", "
        return "%s(%s)" % (self.callee, args_str)


class PrototypeAST(ExprAST):
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    def __str__(self):
        return "[PrototypeAST name=%s, args=%s]" % (self.name, str(self.args))


class FunctionAST(ExprAST):
    def __init__(self, proto: PrototypeAST, body: ExprAST):
        self.proto = proto
        self.body = body

    def __str__(self):
        return "def %s(%s):\n    %s\n\n" % (self.proto.name, ",".join(self.proto.args), str(self.body))


class IfExprAST(ExprAST):
    def __init__(self, cond_expr: ExprAST, then_expr: ExprAST, else_expr: ExprAST):
        self.cond_expr = cond_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __str__(self):
        s = "if (%s):\n        %s\n" % (str(self.cond_expr), str(self.then_expr))
        if self.else_expr is not None:
            s += "else:\n    %s\n" % (str(self.else_expr))
        return s


# Parsing


g_top_level_function_proto = None
g_bin_op_precedence = {
    "=": 2,
    "<": 10,
    ">": 10,
    "+": 20,
    "-": 20,
    "*": 40,
    "/": 40 # highest
}


def parse_identifier_expr(code, ctx) -> Optional[ExprAST]:
    print("parse_identifier_expr")
    id_name = g_identifier_str
    get_next_token(code) # eat identifier

    is_call = False
    if g_cur_token == ".":
        # MemberExpression
        get_next_token(code) # eat '.'
        id_name += "." + g_identifier_str # join MemberExpression, e.g.: class_name="Math", method_name="max", id_name="Math.max"
        print("is_call, id_name=%s" % id_name)
        get_next_token(code) # eat identifier after  after `.`
        is_call = True

    if is_call or g_cur_token == "(":
        # Call
        get_next_token(code) # eat '('
        args = []
        if g_cur_token != ")":
            while True:
                arg = parse_expression(code, ctx)
                if arg is None:
                    print("Error: expected arg expression")
                    return None
                args.append(arg)

                if g_cur_token == ")":
                    break
                if g_cur_token != ",":
                    print("Error: expected ')' or ',' in argument list")
                    return None
                get_next_token(code)

        get_next_token(code) # eat ')'
        print("Found call expr AST: callee=%s, args=%s" % (id_name, args))
        return CallExprAST(callee=id_name, args=args)
    else:
        print("Found variable expr AST, name=%s" % id_name)
        return VariableExprAST(name=id_name)


def parse_number_expr(code, ctx) -> Optional[NumberExprAST]:
    number_expr = NumberExprAST(g_number_val)
    get_next_token(code) # consume the number
    return number_expr


def parse_paren_expr(code, ctx) -> Optional[ExprAST]:
    print("parse_paren_expr")
    get_next_token(code) # eat '('
    v: ExprAST = parse_expression(code, ctx)
    if v is None:
        print("Error: expected expression after '('")
        return None

    if g_cur_token != ")":
        print("Error: expected ')', got: %s, line: %s" % (g_cur_token, code.curline()))
        return None
    get_next_token(code) # eat ')'
    return v


def parse_return_expr(code, ctx) -> Optional[ReturnExprAST]:
    print("parse_return_expr")
    get_next_token(code)  # eat 'return'
    rhs: ExprAST = parse_expression(code, ctx)
    if rhs is None:
        print("Error: expected expression after 'return'")
        return None
    return ReturnExprAST(rhs=rhs)


def parse_variable_declaration_expr(code, ctx) -> Optional[VariableDeclarationExprAST]:
    print("parse_variable_declaration_expr")
    get_next_token(code)  # eat 'var'

    lhs: VariableExprAST = parse_identifier_expr(code, ctx)
    if lhs is None or type(lhs) is not VariableExprAST:
        print("Error: expected a variable name")
        return None

    rhs: BinaryExprAST = parse_bin_op_rhs(code, ctx, 0, lhs)
    if rhs is None:
        print("Error: expected a bin op in variable declaration")
        return None
    return VariableDeclarationExprAST(variable_expr=lhs, rhs=rhs.rhs)


def parse_primary(code, ctx) -> Optional[ExprAST]:
    if g_cur_token == Token.IDENTIFIER:
        return parse_identifier_expr(code, ctx)
    elif g_cur_token == Token.NUMBER:
        return parse_number_expr(code, ctx)
    elif g_cur_token == Token.RETURN:
        return parse_return_expr(code, ctx)
    elif g_cur_token == Token.VAR:
        return parse_variable_declaration_expr(code, ctx)
    elif g_cur_token == Token.IF:
        return parse_if_expr(code, ctx)
    elif g_cur_token == "(":
        return parse_paren_expr(code, ctx)
    print("Error: unknown token(`%s`) when expecting an expression" % g_cur_token)
    return None


def get_token_precedence() -> int:
    if type(g_cur_token) is not str:
        return -1

    if g_cur_token in g_bin_op_precedence:
        token_prec = g_bin_op_precedence[g_cur_token]
    else:
        token_prec = -1
    return token_prec


def parse_bin_op_rhs(code, ctx, expr_prec: int, lhs: ExprAST) -> Optional[ExprAST]:
    print("parse_bin_op_rhs")
    while True:
        token_prec = get_token_precedence()
        if token_prec < expr_prec:
            return lhs

        bin_op = g_cur_token
        get_next_token(code) # eat bin_op

        rhs: ExprAST = parse_primary(code, ctx)
        if rhs is None:
            print("Error: expected rhs of '%s'" % g_cur_token)
            return None

        next_prec = get_token_precedence()
        if token_prec < next_prec:
            rhs = parse_bin_op_rhs(code, ctx, token_prec + 1, rhs)
            if rhs is None:
                print("Error: expected rhs of '%s'" % g_cur_token)
                return None

        lhs = BinaryExprAST(lhs=lhs, op=bin_op, rhs=rhs)


def parse_expression(code, ctx) -> Optional[ExprAST]:
    lhs: ExprAST = parse_primary(code, ctx)
    if lhs is None:
        print("Error: expected a expression on left hand side")
        return None
    rhs = parse_bin_op_rhs(code, ctx, 0, lhs)
    if rhs is None: # e.g.: a()
        return lhs
    return rhs # e.g.: a * 2


def parse_if_expr(code, ctx) -> Optional[ExprAST]:
    print("parse_if_expr")
    get_next_token(code)  # eat `if`

    if g_cur_token != "(":
        print("Error: expected '(' after 'if'")
        return None
    get_next_token(code)  # eat `(`

    cond_expr: ExprAST = parse_expression(code, ctx)
    if cond_expr is None:
        print("Error: expected a expression after 'if'")
        return None

    if g_cur_token != ")":
        print("Error: expected ')' after if cond expr")
        return None
    get_next_token(code)  # eat `)`

    if g_cur_token == "{":
        get_next_token(code) # eat `{` in `if (cond) {`

    then_expr: ExprAST = parse_expression(code, ctx)
    if then_expr is None:
        print("Error: expected then expression after 'if'")
        return None

    if g_cur_token == "}":
        get_next_token(code) # eat `}` in `} else`

    if g_cur_token == Token.ELSE:
        get_next_token(code) # eat `else`
        else_expr: ExprAST = parse_expression(code, ctx)
        if else_expr is None:
            print("Error: expected else expression after 'if'")
            return None
    else:
        else_expr = None

    return IfExprAST(cond_expr=cond_expr, then_expr=then_expr, else_expr=else_expr)


def parse_prototype(code, ctx) -> Optional[PrototypeAST]:
    if g_cur_token != Token.IDENTIFIER:
        print("Error: expected function name in prototype")
        return None

    func_name = g_identifier_str
    get_next_token(code) # eat func_name

    if g_cur_token != "(":
        print("Error: expected '(' in prototype")
        return None

    args = []
    get_next_token(code)
    while g_cur_token == Token.IDENTIFIER or g_cur_token == ",":
        if g_cur_token == Token.IDENTIFIER:
            args.append(g_identifier_str)
        get_next_token(code)

    if g_cur_token != ")":
        print("Error: expected ')' in prototype")
        return None

    get_next_token(code) # eat ")"
    return PrototypeAST(name=func_name, args=args)


def parse_function(code, ctx) -> Optional[FunctionAST]:
    get_next_token(code) # eat `function`
    proto: PrototypeAST = parse_prototype(code, ctx)
    print("Parsed function prototype", proto)
    if proto is None:
        return None

    if g_cur_token != "{":
        print("Error: expected '{' in function, got: %s" % g_last_char)
    get_next_token(code) # eat '{'

    body: ExprAST = parse_expression(code, ctx)
    if body is not None:
        get_next_token(code)
        if g_cur_token != "}":
            print("Error: expected '}' in function, got: %s" % g_last_char)
        get_next_token(code) # eat '}'
        return FunctionAST(proto=proto, body=body)
    return None


def parse_top_level_expr(code, ctx) -> Optional[ExprAST]:
    expr: ExprAST = parse_expression(code, ctx)
    if expr is None:
        print("expected top-level expression")
        return None
    global g_top_level_function_proto
    if g_top_level_function_proto is None:
        g_top_level_function_proto = PrototypeAST("__global", [])
    return FunctionAST(g_top_level_function_proto, expr)


def handle_function(code, ctx):
    print("\nhandle_function")
    func_expr: FunctionAST = parse_function(code, ctx)
    if func_expr is not None:
        ctx['functions'].append(func_expr)
        print("parsed a function definition", func_expr)
    else:
        get_next_token(code)


def handle_top_level_expression(code, ctx):
    print("\nhandle_top_level_expression")
    top_level_expr: ExprAST = parse_top_level_expr(code, ctx)
    if top_level_expr is not None:
        ctx['globals'].append(top_level_expr)
        print("parsed a top-level expr", top_level_expr)
    else:
        get_next_token(code)


# driver

def parse_code_to_ast(code, ctx):
    global g_cur_token
    code = StringBuffer(code)
    get_next_token(code)
    while True:
        if g_cur_token == Token.EOF:
            break
        elif g_cur_token == Token.NEW_LINE:
            get_next_token(code)
        elif g_cur_token == Token.FUNCTION:
            handle_function(code, ctx)
        else:
            handle_top_level_expression(code, ctx)
    return ctx


def main():
    ctx = { "globals": [], "functions": [] }

    filename = "e:\\tmp\\tmp-2021-10\\sample.js"
    with open(filename, "r") as f:
        parse_code_to_ast(f.read(), ctx)

    print("==============================")
    for g in ctx['globals']:
        print(str(g.body))

    print('')
    for function_ast in ctx['functions']:
        print(str(function_ast))


if __name__ == "__main__":
    main()
