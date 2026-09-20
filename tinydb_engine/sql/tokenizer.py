"""
tokenizer.py

Turns a raw SQL string into a list of tokens. This is the lexer it does not understand SQL grammar
at all it just recognizes the smallest meaningful pieces keywords, identifiers, numbers, strings
and punctuation. The parser is what actually understands SQL grammar this stage just splits things
up.
"""
import re
TOKEN_SPEC = [
    ("STRING", r"'[^']*'"),
    ("NUMBER", r"\d+"),
    ("KEYWORD", r"(?i)\b(SELECT|INSERT|INTO|VALUES|WHERE|FROM|CREATE|TABLE|UPDATE|SET|DELETE)\b"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("COMMA", r","),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("EQ", r"="),
    ("STAR", r"\*"),
    ("WHITESPACE", r"\s+"),
]
MASTER_PATTERN = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
TOKEN_REGEX = re.compile(MASTER_PATTERN)
class Token:
    def __init__(self, kind: str, value: str):
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.value!r})"

def tokenize(sql: str) -> list[Token]:
    tokens = []
    pos = 0
    while pos < len(sql):
        match = TOKEN_REGEX.match(sql, pos)
        if not match:
            raise SyntaxError(f"Unexpected character at position {pos}: {sql[pos]!r}")
        kind = match.lastgroup
        value = match.group()
        pos = match.end()
        if kind == "WHITESPACE":
            continue
        if kind == "KEYWORD":
            value = value.upper()
        tokens.append(Token(kind, value))
    return tokens