"""
executor.py

Takes an AST node from parser.py and actually perform it against a BTree. This is where "SQL" ends
and calls into your astorage engine" begins.
A row has multiple columns(id, name, ...) but the BTree only stores one(key, value) blob pair. So a
rows columns are packed into a single value blob here using a seperator byte that would never appear
in normal text data.
"""

from ..storage.btree import BTree
FIELD_SEPERATOR = "\x1f"
class Executor:
    def __init__(self, tree: BTree):
        self.tree = tree
        self.schemas: dict[str, list[str]] = {}

    def execute(self, statement):
        kind = type(statement).__name__
        if kind == "CreateTableStatement":
            return self._execute_create(statement)
        elif kind == "InsertStatement":
            return self._execute_insert(statement)
        elif kind == "SelectStatement":
            return self._execute_select(statement)
        elif kind == "DeleteStatement":
            return self._execute_delete(statement)
        else:
            raise ValueError(f"Unsupported statement type: {kind}")

    def _execute_create(self,stmt) -> None:
        self.schemas[stmt.table_name] = stmt.columns

    def _pack_row(self, values: list) -> bytes:
        return FIELD_SEPERATOR.join(str(v) for v in values).encode()

    def _unpack_row(self, blob: bytes) -> list[str]:
        return blob.decode().split(FIELD_SEPERATOR)

    def _row_key(self, table_name: str, primary_value) -> bytes:
        return f"{table_name}:{primary_value}".encode()

    def _execute_insert(self, stmt) -> None:
        if stmt.table_name not in self.schemas:
            raise ValueError(f"No such table: {stmt.table_name}")
        primary_value = stmt.values[0]
        key = self._row_key(stmt.table_name, primary_value)
        value = self._pack_row(stmt.values)
        self.tree.insert(key, value)

    def _execute_select(self, stmt) -> list[dict]:
        columns = self.schemas.get(stmt.table_name)
        if columns is None:
            raise ValueError(f"No such table: {stmt.table_name}")
        results = []
        if stmt.where_column is None:
            raise NotImplementedError("SELECT without WHERE requires a full table scan not built yet")
        key = self._row_key(stmt.table_name, stmt.where_value)
        raw = self.tree.search(key)
        if raw is not None:
            row_values = self._unpack_row(raw)
            results.append(dict(zip(columns, row_values)))
        return results

    def _execute_delete(self, stmt) -> bool:
        key = self._row_key(stmt.table_name, stmt.where_value)
        return self.tree.delete(key)
    