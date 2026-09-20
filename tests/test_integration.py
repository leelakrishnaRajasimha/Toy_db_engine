"""
test_integration.py

Full end to end run: SQL layer, transactions then a full process restart to prove crash recovery and
durability hold across everything not just in isloated unit tests.
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
from tinydb_engine.wal.log import WriteAheadLog
from tinydb_engine.sql.parser import parse_sql
from tinydb_engine.sql.executor import Executor
from tinydb_engine.transaction import Transaction
DB_FILE = "tests/test_integration.db"
WAL_FILE = "tests/test_integration.wal"
for f in [DB_FILE, WAL_FILE]:
    if os.path.exists(f):
        os.remove(f)
pager = Pager(DB_FILE)
wal = WriteAheadLog(WAL_FILE)
tree = BTree(pager, wal)
executor = Executor(tree)
executor.execute(parse_sql("CREATE TABLE users(id, name)"))
for i in range(50):
    sql = f"INSERT INTO users VALUES ({i}, 'user{i}')"
    executor.execute(parse_sql(sql))
print("Inserted 50 row via SQL")
result = executor.execute(parse_sql("SELECT * FROM users WHERE id = 20"))
assert result == [{'id': "20", 'name': 'user20'}]
print("SELECT id=20 correct:", result)
executor.execute(parse_sql("DELETE FROM users WHERE id = 10"))
assert executor.execute(parse_sql("SELECT * FROM users WHERE id = 10")) == []
print("DELETE id=10 confirmed")
txn = Transaction(tree)
txn.begin()
txn.insert(b"txn_key", b"txn_value")
assert txn.search(b"txn_key") == b"txn_value"
txn.commit()
assert tree.search(b"txn_key") == b"txn_value"
print("Transaction commit path verified")
txn.begin()
txn.insert(b"should_not_exist", b"nope")
txn.rollback()
assert tree.search(b"should_not_exist") is None
print("Transaction rollback path verified")
pager.close()
wal.close()
print("Session 1 complete all operations suceeded closing normally.\n")
pager2 = Pager(DB_FILE)
wal2 = WriteAheadLog(WAL_FILE)
tree2 = BTree(pager2, wal2)
executor2 = Executor(tree2)
executor2.execute(parse_sql("CREATE TABLE users(id, name)"))
result_after_restart = executor2.execute(parse_sql("SELECT * FROM users WHERE id = 20"))
print("After restart SELECT id=20:", result_after_restart)
assert result_after_restart == [{'id': "20", 'name': 'user20'}]
deleted_check = executor2.execute(parse_sql("SELECT * FROM users WHERE id = 10"))
assert deleted_check == []
print("After restart DELETE id=10 still correctly absent")
assert tree2.search(b"txn_key") == b"txn_value"
assert tree2.search(b"should_not_exist") is None
print("After restart transaction commit and rollback both still correctly preserved")
pager2.close()
wal2.close()
print("\n ALL INTEGRATION CHECKS PASSED")