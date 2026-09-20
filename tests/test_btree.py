"""
test_btree.py

Verifies core B-tree behaviour insert, search, delete, and splitting when a leaf page overflows.
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
from tinydb_engine.wal.log import WriteAheadLog
DB_FILE = "tests/test_btree.db"
WAL_FILE = "tests/test_btree.wal"
for f in (DB_FILE, WAL_FILE):
    if os.path.exists(f):
        os.remove(f)
pager = Pager(DB_FILE)
wal = WriteAheadLog(WAL_FILE)
tree = BTree(pager, wal)
for i in range(200):
    key = f"key{i:04d}".encode()
    value = f"value{i:04d}".encode()
    tree.insert(key, value)
print("Inserted 200 keys.")
result_low = tree.search(b"key0005")
print("key0005 ->", result_low)
assert result_low == b"value0005"

result_high = tree.search(b"key0195")
print("key0195 ->", result_high)
assert result_high == b"value0195"

tree.delete(b"key0005")
assert tree.search(b"key0005") is None
print("key0005 deleted successfully.")

tree.delete(b"key0195")
assert tree.search(b"key0195") is None
print("key0195 deleted successfully.")

pager.close()
wal.close()
print("ALL BTREE CHECKS PASSED")