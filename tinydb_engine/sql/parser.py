"""
parser.py

Consumes the flat token list from tokenizer.py and produces a small AST(Abstract Syntax Tree) node 
describing the statement. Each node type below is deliberately just a plain container of the fields
the executor will need the parsers only job is figuring out which fields exist and in what order
not what to do with them.
"""

from .tokenizer import Token, tokenize
class CreateTableStatement:
    def __init__(self, table_name: str, columns: list[str]):
        self.table_name = table_name
        self.columns = columns

    def __repr__(self) -> str:
        return f"CreateTable({self.table_name}, {self.columns})"

class InsertStatement:
    def __init__(self, table_name: str, values: list):
        self.table_name = table_name
        self.values = values

    def __repr__(self) -> str:
        return f"Insert({self.table_name}, {self.values})"

class SelectStatement:
    def __init__(self, table_name: str, where_column: str | None, where_value):
        self.table_name = table_name
        self.where_column = where_column
        self.where_value = where_value

    def __repr__(self) -> str:
        return f"Select({self.table_name}, WHERE {self.where_column} = {self.where_value})"

class DeleteStatement:
    def __init__(self, table_name: str, where_column: str, where_value):
        self.table_name = table_name
        self.where_column = where_column
        self.where_value = where_value

    def __repr__(self) -> str:
        return f"Delete({self.table_name}, WHERE {self.where_column} = {self.where_value})"

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _expect(self, kind: str, value: str | None = None) -> Token:
        token = self._peek()
        if token is None or token.kind != kind or (value is not None and token.value != value):
            raise SyntaxError(f"Expected {kind} {value or ''}, got {token}")
        return self._advance()

    def parse(self):
        first = self._peek()
        if first is None:
            raise SyntaxError("Empty staement")
        if first.value == "CREATE":
            return self._parse_create()
        elif first.value == "INSERT":
            return self._parse_insert()
        elif first.value == "SELECT":
            return self._parse_select()
        elif first.value == "DELETE":
            return self._parse_delete()
        else:
            raise SyntaxError(f"Unsupported statement start: {first}")

    def _parse_create(self) -> CreateTableStatement:
        self._expect("KEYWORD", "CREATE")
        self._expect("KEYWORD", "TABLE")
        table_name = self._expect("IDENT").value
        self._expect("LPAREN")
        columns = [self._expect("IDENT").value]
        while self._peek() and self._peek().kind == "COMMA":
            self._advance()
            columns.append(self._expect("IDENT").value)
        self._expect("RPAREN")
        return CreateTableStatement(table_name, columns)

    def _parse_insert(self) -> InsertStatement:
        self._expect("KEYWORD", "INSERT")
        self._expect("KEYWORD", "INTO")
        table_name = self._expect("IDENT").value
        self._expect("KEYWORD", "VALUES")
        self._expect("LPAREN")
        values = [self._parse_literal()]
        while self._peek() and self._peek().kind == "COMMA":
            self._advance()
            values.append(self._parse_literal())
        self._expect("RPAREN")
        return InsertStatement(table_name, values)

    def _parse_select(self) -> SelectStatement:
        self._expect("KEYWORD", "SELECT")
        self._expect("STAR")
        self._expect("KEYWORD", "FROM")
        table_name = self._expect("IDENT").value
        where_column, where_value = None, None
        if self._peek() and self._peek().value == "WHERE":
            self._advance()
            where_column = self._expect("IDENT").value
            self._expect("EQ")
            where_value = self._parse_literal()
        return SelectStatement(table_name, where_column, where_value)

    def _parse_delete(self) -> DeleteStatement:
        self._expect("KEYWORD", "DELETE")
        self._expect("KEYWORD", "FROM")
        table_name = self._expect("IDENT").value
        self._expect("KEYWORD", "WHERE")
        where_column = self._expect("IDENT").value
        self._expect("EQ")
        where_value = self._parse_literal()
        return DeleteStatement(table_name, where_column, where_value)

    def _parse_literal(self):
        token = self._advance()
        if token.kind == "NUMBER":
            return int(token.value)
        elif token.kind == "STRING":
            return token.value.strip("'")
        else:
            raise SyntaxError(f"Expected a literal value, got {token}")

def parse_sql(sql: str):
    tokens = tokenize(sql)
    return Parser(tokens).parse()