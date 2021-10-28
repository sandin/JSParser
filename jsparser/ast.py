from typing import List


class ExprAST(object):
    pass


class NumberExprAST(ExprAST):
    """
    e.g.:
        a = 1.0
             ^
           value
    """
    def __init__(self, value: float):
        self.value = value

    def __str__(self):
        return "%s" % (self.value,)


class VariableExprAST(ExprAST):
    """
    e.g.:
        a = 1.0
        ^
       name
    """
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return "%s" % (self.name,)


class BinaryExprAST(ExprAST):
    """
    e.g.:
        a  = 1.0
        ^  ^  ^
       lhs | rhs
           op
    """
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
    """
    e.g.:
        var a = 1.0;
            ^    ^
            |   rhs
        variable_expr
    """
    def __init__(self, variable_expr: VariableExprAST, rhs: ExprAST):
        BinaryExprAST.__init__(self, variable_expr, "=", rhs)


class ReturnExprAST(ExprAST):
    """
    e.g.:
        return 1.0
                ^
               rhs
    """
    def __init__(self, rhs: ExprAST):
        self.rhs = rhs

    def __str__(self):
        return "return %s" % (str(self.rhs),)


class CallExprAST(ExprAST):
    """
    e.g.:
        init(arg0,   arg1);
         ^    ^        ^
         |    |- args -|
      callee
    """
    def __init__(self, callee: str, args: List[ExprAST]):
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
    """
    e.g.:
        function init(arg0,   arg1) {
                  ^    ^        ^
                  |    |- args -|
                 name
    """
    def __init__(self, name: str, args: List[str]):
        self.name = name
        self.args = args

    def __str__(self):
        return "[PrototypeAST name=%s, args=%s]" % (self.name, str(self.args))


class FunctionAST(ExprAST):
    """
    e.g.:
        function init(arg0, arg1) {
            var a = arg0 + arg1;            // <- body
        }
    """
    def __init__(self, proto: PrototypeAST, body: ExprAST):
        self.proto = proto
        self.body = body

    def __str__(self):
        print("self.body", self.body)
        return "def %s(%s):\n%s\n\n" % (self.proto.name, ",".join(self.proto.args), str(self.body))


class IfExprAST(ExprAST):
    """
    e.g.:
        if (a == 0.0) {   // <- cond_expr
            b = 0.0;      // <- then_expr
        } else {
            b = 1.0;      // <- else_expr
        }
    """
    def __init__(self, cond_expr: ExprAST, then_expr: ExprAST, else_expr: ExprAST):
        self.cond_expr = cond_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __str__(self):
        s = "if (%s):\n%s\n" % (str(self.cond_expr), str(self.then_expr))
        if self.else_expr is not None:
            s += "else:\n%s\n" % (str(self.else_expr))
        return s


class BlockExprAST(ExprAST):
    """
    e.g.:
        {
            a = 0.0;               // <- body_expr
         ^
      indent
        }
    """
    def __init__(self, indent: int, body_expr: List[ExprAST]):
        self.indent = indent
        self.body_expr = body_expr

    def __str__(self):
        indent = "".join(map(lambda i: " ", range(0, self.indent * 4)))
        s = ""
        for expr in self.body_expr:
            s += indent + str(expr) + "\n"
        return s
