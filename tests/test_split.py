"""
test_split.py

Manual sanity check insert enough keys to force a leaf split then verify search and delete still 
work correctly on both sides.
"""

import os
from tinydb_engine.storage.pager import Pager
from tinydb_engine.storage.btree import BTree
DB_FILE = "tests/test_split.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
pager = Pager(DB_FILE)
tree = BTree(pager)
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
print("ALL CHECKS PASSED")