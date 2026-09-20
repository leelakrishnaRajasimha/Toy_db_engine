"""
test_executor.py

End to end SQL test create a table, insert rows, select by key, delete a row
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
from tinydb_engine.wal.log import WriteAheadLog
from tinydb_engine.sql.parser import parse_sql
from tinydb_engine.sql.executor import Executor
DB_FILE = "tests/test_executor.db"
WAL_FILE = "tests/test_executor.wal"
for f in [DB_FILE, WAL_FILE]:
    if os.path.exists(f):
        os.remove(f)
pager = Pager(DB_FILE)
wal = WriteAheadLog(WAL_FILE)
tree = BTree(pager, wal)
executor = Executor(tree)
executor.execute(parse_sql("CREATE TABLE users(id, name)"))
executor.execute(parse_sql("INSERT INTO users VALUES (1, 'raj')"))
executor.execute(parse_sql("INSERT INTO users VALUES (2, 'sam')"))
result = executor.execute(parse_sql("SELECT * FROM users WHERE id = 1"))
print("SELECT id=1:", result)
assert result == [{'id': "1", 'name': 'raj'}]
result2 = executor.execute(parse_sql("SELECT * FROM users WHERE id = 2"))
print("SELECT id=2:", result2)
assert result2 == [{'id': "2", 'name': 'sam'}]
executor.execute(parse_sql("DELETE FROM users WHERE id = 1"))
result3 = executor.execute(parse_sql("SELECT * FROM users WHERE id = 1"))
print("SELECT id=1 after DELETE:", result3)
assert result3 == []
pager.close()
wal.close()
print("ALL EXECUTOR CHECKS PASSED")
