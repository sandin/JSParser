from typing import Optional
from . import ast
from . import lexer


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
g_block_level = 0


def parse_identifier_expr(code, ctx) -> Optional[ast.ExprAST]:
    print("parse_identifier_expr")
    id_name = lexer.g_identifier_str
    lexer.get_next_token(code) # eat identifier

    is_call = False
    if lexer.g_cur_token == ".":
        # MemberExpression
        lexer.get_next_token(code) # eat '.'
        id_name += "." + lexer.g_identifier_str # join MemberExpression, e.g.: class_name="Math", method_name="max", id_name="Math.max"
        print("is_call, id_name=%s" % id_name)
        lexer.get_next_token(code) # eat identifier after  after `.`
        is_call = True

    id_name = map_symbol(id_name, ctx)

    if is_call or lexer.g_cur_token == "(":
        # Call
        lexer.get_next_token(code) # eat '('
        args = []
        if lexer.g_cur_token != ")":
            while True:
                arg = parse_expression(code, ctx)
                if arg is None:
                    print("Error: expected arg expression")
                    return None
                args.append(arg)

                if lexer.g_cur_token == ")":
                    break
                if lexer.g_cur_token != ",":
                    print("Error: expected ')' or ',' in argument list")
                    return None
                lexer.get_next_token(code)

        lexer.get_next_token(code) # eat ')'
        print("Found call expr AST: callee=%s, args=%s" % (id_name, args))
        return ast.CallExprAST(callee=id_name, args=args)
    else:
        print("Found variable expr AST, name=%s" % id_name)
        return ast.VariableExprAST(name=id_name)


def map_symbol(symbol_name, ctx):
    if "externals" in ctx and symbol_name in ctx['externals']:
        return ctx['externals'][symbol_name]
    return symbol_name


def parse_number_expr(code, ctx) -> Optional[ast.NumberExprAST]:
    number_expr = ast.NumberExprAST(lexer.g_number_val)
    lexer.get_next_token(code)  # consume the number
    return number_expr


def parse_paren_expr(code, ctx) -> Optional[ast.ExprAST]:
    print("parse_paren_expr")
    lexer.get_next_token(code)  # eat '('
    v: ast.ExprAST = parse_expression(code, ctx)
    if v is None:
        print("Error: expected expression after '('")
        return None

    if lexer.g_cur_token != ")":
        print("Error: expected ')', got: %s, line: %s" % (lexer.g_cur_token, code.curline()))
        return None
    lexer.get_next_token(code) # eat ')'
    return v


def parse_return_expr(code, ctx) -> Optional[ast.ReturnExprAST]:
    print("parse_return_expr")
    lexer.get_next_token(code)  # eat 'return'
    rhs: ast.ExprAST = parse_expression(code, ctx)
    if rhs is None:
        print("Error: expected expression after 'return'")
        return None
    return ast.ReturnExprAST(rhs=rhs)


def parse_variable_declaration_expr(code, ctx) -> Optional[ast.VariableDeclarationExprAST]:
    print("parse_variable_declaration_expr")
    lexer.get_next_token(code)  # eat 'var'

    lhs: ast.VariableExprAST = parse_identifier_expr(code, ctx)
    if lhs is None or type(lhs) is not ast.VariableExprAST:
        print("Error: expected a variable name")
        return None

    rhs: ast.BinaryExprAST = parse_bin_op_rhs(code, ctx, 0, lhs)
    if rhs is None:
        print("Error: expected a bin op in variable declaration")
        return None
    return ast.VariableDeclarationExprAST(variable_expr=lhs, rhs=rhs.rhs)


def parse_primary(code, ctx) -> Optional[ast.ExprAST]:
    if lexer.g_cur_token == lexer.Token.IDENTIFIER:
        return parse_identifier_expr(code, ctx)
    elif lexer.g_cur_token == lexer.Token.NUMBER:
        return parse_number_expr(code, ctx)
    elif lexer.g_cur_token == lexer.Token.RETURN:
        return parse_return_expr(code, ctx)
    elif lexer.g_cur_token == lexer.Token.VAR:
        return parse_variable_declaration_expr(code, ctx)
    elif lexer.g_cur_token == lexer.Token.IF:
        return parse_if_expr(code, ctx)
    elif lexer.g_cur_token == "(":
        return parse_paren_expr(code, ctx)
    elif lexer.g_cur_token == "{":
        return parse_block_expr(code, ctx)
    print("Error: unknown token(`%s`) when expecting an expression" % lexer.g_cur_token)
    return None


def get_token_precedence() -> int:
    if type(lexer.g_cur_token) is not str:
        return -1

    if lexer.g_cur_token in g_bin_op_precedence:
        token_prec = g_bin_op_precedence[lexer.g_cur_token]
    else:
        token_prec = -1
    return token_prec


def parse_bin_op_rhs(code, ctx, expr_prec: int, lhs: ast.ExprAST) -> Optional[ast.ExprAST]:
    print("parse_bin_op_rhs")
    while True:
        token_prec = get_token_precedence()
        if token_prec < expr_prec:
            return lhs

        bin_op = lexer.g_cur_token
        lexer.get_next_token(code)  # eat bin_op

        rhs: ast.ExprAST = parse_primary(code, ctx)
        if rhs is None:
            print("Error: expected rhs of '%s'" % lexer.g_cur_token)
            return None

        next_prec = get_token_precedence()
        if token_prec < next_prec:
            rhs = parse_bin_op_rhs(code, ctx, token_prec + 1, rhs)
            if rhs is None:
                print("Error: expected rhs of '%s'" % lexer.g_cur_token)
                return None

        lhs = ast.BinaryExprAST(lhs=lhs, op=bin_op, rhs=rhs)


def parse_expression(code, ctx) -> Optional[ast.ExprAST]:
    print("parse_expression")
    lhs: ast.ExprAST = parse_primary(code, ctx)
    if lhs is None:
        print("Error: expected a expression on left hand side")
        return None
    rhs = parse_bin_op_rhs(code, ctx, 0, lhs)
    if rhs is None:  # e.g.: a()
        return lhs
    return rhs  # e.g.: a * 2


def parse_if_expr(code, ctx) -> Optional[ast.ExprAST]:
    print("parse_if_expr")
    lexer.get_next_token(code)  # eat `if`

    if lexer.g_cur_token != "(":
        print("Error: expected '(' after 'if'")
        return None
    lexer.get_next_token(code)  # eat `(`

    cond_expr: ast.ExprAST = parse_expression(code, ctx)
    if cond_expr is None:
        print("Error: expected a expression after 'if'")
        return None

    if lexer.g_cur_token != ")":
        print("Error: expected ')' after if cond expr")
        return None
    lexer.get_next_token(code)  # eat `)`

    then_expr: ast.ExprAST = parse_expression(code, ctx)
    if then_expr is None:
        print("Error: expected then expression after 'if'")
        return None

    if lexer.g_cur_token == lexer.Token.ELSE:
        lexer.get_next_token(code)  # eat `else`
        else_expr: ast.ExprAST = parse_expression(code, ctx)
        if else_expr is None:
            print("Error: expected else expression after 'if'")
            return None
    else:
        else_expr = None

    return ast.IfExprAST(cond_expr=cond_expr, then_expr=then_expr, else_expr=else_expr)


def parse_prototype(code, ctx) -> Optional[ast.PrototypeAST]:
    if lexer.g_cur_token != lexer.Token.IDENTIFIER:
        print("Error: expected function name in prototype")
        return None

    func_name = lexer.g_identifier_str
    lexer.get_next_token(code)  # eat func_name

    if lexer.g_cur_token != "(":
        print("Error: expected '(' in prototype")
        return None

    args = []
    lexer.get_next_token(code)
    while lexer.g_cur_token == lexer.Token.IDENTIFIER or lexer.g_cur_token == ",":
        if lexer.g_cur_token == lexer.Token.IDENTIFIER:
            args.append(lexer.g_identifier_str)
        lexer.get_next_token(code)

    if lexer.g_cur_token != ")":
        print("Error: expected ')' in prototype")
        return None

    lexer.get_next_token(code)  # eat ")"
    return ast.PrototypeAST(name=func_name, args=args)


def parse_block_expr(code, ctx) -> Optional[ast.BlockExprAST]:
    global g_block_level
    print("parse_block_expr", g_block_level)
    body_expr = []
    lexer.get_next_token(code)  # eat '{'

    g_block_level += 1
    while lexer.g_cur_token != lexer.Token.EOF and lexer.g_cur_token != lexer.Token.FUNCTION and lexer.g_cur_token != "}":
        expr: ast.ExprAST = parse_expression(code, ctx)
        if expr is None:
            print("Error: expected expression in block")
            return None
        print("\tappend block expr", expr, g_block_level)
        body_expr.append(expr)
        lexer.get_next_token(code)

    print("/parse_block_expr")
    block = ast.BlockExprAST(g_block_level, body_expr=body_expr)
    g_block_level -=1
    return block


def parse_function(code, ctx) -> Optional[ast.FunctionAST]:
    lexer.get_next_token(code)  # eat `function`
    proto: ast.PrototypeAST = parse_prototype(code, ctx)
    print("Parsed function prototype", proto)
    if proto is None:
        return None

    if lexer.g_cur_token != "{":
        print("Error: expected '{' in function, got: %s" % lexer.g_last_char)

    body: ast.ExprAST = parse_block_expr(code, ctx)
    if body is not None:
        if lexer.g_cur_token != lexer.Token.FUNCTION:  # in case missing ";" end of line
            lexer.get_next_token(code)
        return ast.FunctionAST(proto=proto, body=body)
    else:
        return None


def parse_top_level_expr(code, ctx) -> Optional[ast.ExprAST]:
    expr: ast.ExprAST = parse_expression(code, ctx)
    if expr is None:
        print("expected top-level expression")
        return None
    global g_top_level_function_proto
    if g_top_level_function_proto is None:
        g_top_level_function_proto = ast.PrototypeAST("__global", [])
    return ast.FunctionAST(g_top_level_function_proto, expr)


def handle_function(code, ctx):
    print("\nhandle_function")
    func_expr: ast.FunctionAST = parse_function(code, ctx)
    if func_expr is not None:
        ctx['functions'].append(func_expr)
        print("parsed a function definition", func_expr)
    else:
        lexer.get_next_token(code)


def handle_top_level_expression(code, ctx):
    print("\nhandle_top_level_expression, lexer.g_cur_token=", lexer.g_cur_token)
    top_level_expr: ast.ExprAST = parse_top_level_expr(code, ctx)
    if top_level_expr is not None:
        ctx['globals'].append(top_level_expr)
        print("parsed a top-level expr", top_level_expr)
    else:
        lexer.get_next_token(code)


def parse_code_to_ast(code, ctx):
    global g_cur_token
    code = lexer.StringBuffer(code)
    lexer.get_next_token(code)
    while True:
        if lexer.g_cur_token == lexer.Token.EOF:
            break
        elif lexer.g_cur_token == lexer.Token.NEW_LINE:
            lexer.get_next_token(code)
        elif lexer.g_cur_token == lexer.Token.FUNCTION:
            handle_function(code, ctx)
        else:
            handle_top_level_expression(code, ctx)
    return ctx
