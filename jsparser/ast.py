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