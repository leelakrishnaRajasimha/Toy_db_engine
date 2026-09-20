"""
test_recovery.py

Simulates a crash write to the WAL and Pages then reopen everything fresh(as if the process 
restarted) and confirm the data is still there and the WAL got checkpointed after recovery ran.
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
from tinydb_engine.wal.log import WriteAheadLog
DB_FILE = "tests/test_recovery.db"
WAL_FILE = "tests/test_recovery.wal"
for f in (DB_FILE, WAL_FILE):
    if os.path.exists(f):
        os.remove(f)
pager = Pager(DB_FILE)
wal = WriteAheadLog(WAL_FILE)
tree = BTree(pager, wal)
tree.insert(b"x", b"first")
tree.insert(b"y", b"second")
pager.close()
wal.close()
pager2 = Pager(DB_FILE)
wal2 = WriteAheadLog(WAL_FILE)
tree2 = BTree(pager2, wal2)
assert tree2.search(b"x") == b"first"
assert tree2.search(b"y") == b"second"
print("Recovered data correctly:", tree2.search(b"x"), tree2.search(b"y"))
remaining = list(wal2.replay())
assert remaining == []
print("WAL correctly cleared after checkpoint.")
pager2.close()
wal2.close()
print("ALL RECOVERY CHECKS PASSED")