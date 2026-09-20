"""
engine.py

The single public entry point for the whole project. Everywhere else is an internal building block
this is the one class meant to actually be imported and used.
Without this using the engine means manualky wiring up four seperate objects every time.
"""

from .storage.pager import Pager
from .storage.btree import BTree
from .wal.log import WriteAheadLog
from .sql.parser import parse_sql
from .sql.executor import Executor
class Engine:
    def __init__(self, db_path: str):
        wal_path = db_path.rsplit(".", 1)[0] + ".wal" if "." in db_path else db_path + ".wal"
        self.pager = Pager(db_path)
        self.wal = WriteAheadLog(wal_path)
        self.tree = BTree(self.pager, self.wal)
        self.executor = Executor(self.tree)

    def execute(self, sql: str):
        statement = parse_sql(sql)
        return self.executor.execute(statement)

    def close(self):
        self.pager.close()
        self.wal.close()

    def __enter__(self) -> "Engine":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()