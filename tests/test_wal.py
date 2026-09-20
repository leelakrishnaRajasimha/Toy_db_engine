"""
test_wal.py

Verifies the Write Ahead Log(WAL) itself every insert/delete gets appended correctly and replaying
the log back gives the exact same sequence of operations that were originally logged.
"""

import os
from tinydb_engine.wal.log import WriteAheadLog, OP_INSERT, OP_DELETE
WAL_FILE = "tests/test_wal.wal"
if os.path.exists(WAL_FILE):
    os.remove(WAL_FILE)
wal = WriteAheadLog(WAL_FILE)
wal.log_insert(b"apple", b"red fruit")
wal.log_insert(b"banana", b"yellow fruit")
wal.log_delete(b"apple")
wal.close()
wal2 = WriteAheadLog(WAL_FILE)
entries = list(wal2.replay())
print("Replayed entries are:", entries)
assert entries[0] == (OP_INSERT, b"apple", b"red fruit")
assert entries[1] == (OP_INSERT, b"banana", b"yellow fruit")
assert entries[2] == (OP_DELETE, b"apple", b"")
wal2.close()
print("ALL WAL CHECKS PASSED")

