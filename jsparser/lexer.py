import enum

g_last_char: str = ' '
g_identifier_str: str = None
g_number_val: float = 0
g_cur_token = None


def reset():
    global g_last_char, g_identifier_str, g_number_val, g_cur_token
    g_last_char = ' '
    g_identifier_str = None
    g_number_val = 0
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
    #BLOCK = -11
    #PAREN = -12


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
        return None  # EOF

    def eof(self):
        return self._index == self._length - 1

    def curline(self):
        start_index = self._index
        c = self._value[start_index]
        while c != "\r" and c != "\n" and start_index > 0:
            c = self._value[start_index]
            start_index -= 1
        if start_index > 0:
            start_index += 1  # skip the nl
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

    if g_last_char is None:  # EOF
        return Token.EOF

    if g_last_char.isalpha() or g_last_char == "_":  # identifier: [a-zA-Z][a-zA-Z0-9]*
        g_identifier_str = g_last_char
        g_last_char = code.getchar()
        while g_last_char.isalnum() or g_last_char == "_":
            g_identifier_str += g_last_char
            g_last_char = code.getchar()
        if g_identifier_str in g_keywords:
            return g_keywords[g_identifier_str]
        return Token.IDENTIFIER

    if g_last_char.isdigit():  # Number: [0-9.]
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
            while g_last_char and g_last_char != "\n" and g_last_char != "\r":
                g_last_char = code.getchar()

            if g_last_char:
                return get_token(code)

    if g_last_char == "\r" or g_last_char == "\n" or g_last_char == ";":
        print("eat nl", g_last_char)
        g_last_char = code.getchar()  # eat nl
        #while g_last_char == "\r" or g_last_char == "\n" or g_last_char == ";":
        #    print("eat nl2", g_last_char)
        #    g_last_char = code.getchar()
        return Token.NEW_LINE

    #if g_last_char == "{":
    #    g_last_char = code.getchar()  # eat `{`
    #    return Token.BLOCK

    #if g_last_char == "(":
    #    g_last_char = code.getchar()  # eat `(`
    #    return Token.PAREN

    this_char = g_last_char
    g_last_char = code.getchar()
    return this_char


def get_next_token(code: StringBuffer):
    global g_cur_token
    g_cur_token = get_token(code)
    print("[Token] get_next_token, g_cur_token=%s, g_last_char=%s, g_identifier_str=%s, g_number_val=%d" % (g_cur_token, g_last_char, g_identifier_str, g_number_val))
    return g_cur_token
