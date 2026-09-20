"""
transaction.py

A minimal transaction layer sitting on top of the BTree. While a transaction is open writes are
buffered in memory only nothing touches the WAL or the real pages yet. COMMIT replays the buffer
through the trees real insert/delete . ROLLBACK just discards the buffer.
This is deliberately simple no isolation between concurrent transactions no partial commit handling.
"""

from .storage.btree import BTree
OP_INSERT = "insert"
OP_DELETE = "delete"
class TransactionError(Exception):
    pass
class Transaction:
    def __init__(self, tree: BTree):
        self.tree = tree
        self.active = False
        self.buffer: list[tuple[str, bytes, bytes | None]] = []

    def begin(self) -> None:
        if self.active:
            raise TransactionError("A transaction is already open")
        self.active = True
        self.buffer = []

    def insert(self, key: bytes, value: bytes) -> None:
        if not self.active:
            raise TransactionError("No open transaction call begin() first")
        self.buffer.append((OP_INSERT, key, value))

    def delete(self, key: bytes) -> None:
        if not self.active:
            raise TransactionError("No open transaction call begin() first")
        self.buffer.append((OP_DELETE, key, None))

    def search(self, key: bytes) -> bytes | None:
        for op, buffered_key, value in reversed(self.buffer):
            if buffered_key == key:
                return value if op == OP_INSERT else None
        return self.tree.search(key)

    def commit(self) -> None:
        if not self.active:
            raise TransactionError("No open transaction to commit")
        for op, key, value in self.buffer:
            if op == OP_INSERT:
                self.tree.insert(key, value)
            else:
                self.tree.delete(key)
        self.buffer = []
        self.active = False

    def rollback(self) -> None:
        if not self.active:
            raise TransactionError("No open transaction to roll back")
        self.buffer = []
        self.active = False