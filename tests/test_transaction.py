"""
test_transaction.py

Verifies writes inside an open transaction are visible to reads within that same transaction but
do not touch the real tree until commit rollback discards everything with no trace.
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
from tinydb_engine.wal.log import WriteAheadLog
from tinydb_engine.transaction import Transaction
DB_FILE = "tests/test_transaction.db"
WAL_FILE = "tests/test_transaction.wal"
for f in (DB_FILE, WAL_FILE):
    if os.path.exists(f):
        os.remove(f)
pager = Pager(DB_FILE)
wal = WriteAheadLog(WAL_FILE)
tree = BTree(pager, wal)
txn = Transaction(tree)
txn.begin()
txn.insert(b"a", b"apple")
print("Inside txn, before commit:", txn.search(b"a"))
assert txn.search(b"a") == b"apple"
assert tree.search(b"a") is None
txn.commit()
print("After commit, real tree:", tree.search(b"a"))
assert tree.search(b"a") == b"apple"
txn.begin()
txn.insert(b"b", b"banana")
assert txn.search(b"b") == b"banana"
txn.rollback()
assert txn.search(b"b") is None
print("After rollback, 'b' exists on real tree:", tree.search(b"b"))
pager.close()
wal.close()
print("ALL TRANSACTION CHECKS PASSED")