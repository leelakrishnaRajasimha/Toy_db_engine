"""
btree.py

A B-tree where the root may be a leaf(small tree) or an internal routing page. Internal pages are 
kept in memory only for now leaves are the only thing on disk. This is a deliberate simplification
to get splitting working first, persistent internal pages comes later.
"""

from .page import Page, PAGE_TYPE_INTERNAL, PAGE_TYPE_LEAF
from .pager import Pager
from tinydb_engine import wal
from ..wal.log import WriteAheadLog, OP_INSERT, OP_DELETE
class BTree:
    def __init__(self, pager: Pager, wal: WriteAheadLog) -> None:
        self.pager = pager
        self.wal = wal
        if self.pager.num_pages == 0:
            root = Page(PAGE_TYPE_LEAF)
            self.pager.allocate_page(root)
        self.root = self.pager.read_page(0) if self._root_is_page_0() else None
        self.root_page_num = 0
        self._recover_from_wal()

    def _root_is_page_0(self) -> bool:
        return not hasattr(self, "_in_memory_root")

    def insert(self, key: bytes, value: bytes) -> None:
        self.wal.log_insert(key, value)
        self._apply_insert(key, value)
        
    def _apply_insert(self, key: bytes, value: bytes) -> None:
        root = self._get_root()
        if root.is_leaf():
            self._insert_into_leaf(root, self.root_page_num, key, value)
        else:
            self._insert_via_internal(root, key, value)

    def _get_root(self) -> Page:
        if hasattr(self, "_in_memory_root"):
            return self._in_memory_root
        return self.pager.read_page(self.root_page_num)

    def _insert_into_leaf(self, leaf: Page, page_num: int, key: bytes, value: bytes) -> None:
        leaf.insert_cell(key, value)
        if not leaf.is_full():
            self.pager.write_page(page_num, leaf)
            return
        left, right, promoted_key = self._split_leaf(leaf)
        left_num = page_num
        self.pager.write_page(left_num, left)
        right_num = self.pager.allocate_page(right)
        new_root = Page(PAGE_TYPE_INTERNAL)
        new_root.cells = [(promoted_key, "b")]
        new_root.children = [left_num, right_num]
        self._in_memory_root = new_root

    def _split_leaf(self, leaf: Page) -> tuple[Page, Page, bytes]:
        mid = len(leaf.cells) // 2
        left = Page(PAGE_TYPE_LEAF)
        left.cells = leaf.cells[:mid]
        right = Page(PAGE_TYPE_LEAF)
        right.cells = leaf.cells[mid:]
        promoted_key = right.cells[0][0]
        return left, right, promoted_key

    def _insert_via_internal(self, root: Page, key: bytes, value: bytes) -> None:
        child_index = self._find_child_index(root, key)
        child_page_num = root.children[child_index]
        child = self.pager.read_page(child_page_num)
        self._insert_into_leaf(child, child_page_num, key, value)

    def _find_child_index(self, internal: Page, key: bytes) -> int:
        for i, (separator_key, _) in enumerate(internal.cells):
            if key < separator_key:
                return i
        return len(internal.cells)

    def search(self, key: bytes) -> bytes | None:
        root = self._get_root()
        if root.is_leaf():
            return root.find_cell(key)
        child_index = self._find_child_index(root, key)
        child_page_num = root.children[child_index]
        child = self.pager.read_page(child_page_num)
        return child.find_cell(key)

    def delete(self, key: bytes) -> bool:
        self.wal.log_delete(key)
        root = self._get_root()
        if root.is_leaf():
            deleted = root.delete_cell(key)
            if deleted:
                self.pager.write_page(self.root_page_num, root)
            return deleted
        child_index = self._find_child_index(root, key)
        child_page_num = root.children[child_index]
        child = self.pager.read_page(child_page_num)
        deleted = child.delete_cell(key)
        if deleted:
            self.pager.write_page(child_page_num, child)
        return deleted

    def _recover_from_wal(self) -> None:
        entries = list(self.wal.replay())
        if not entries:
            return
        for op, key, value in entries:
            if op == OP_INSERT:
                self._apply_insert(key, value)
            elif op == OP_DELETE:
                root = self._get_root()
                if root.is_leaf():
                    root.delete_cell(key)
                    self.pager.write_page(self.root_page_num, root)
                else:
                    child_index = self._find_child_index(root, key)
                    child_page_num = root.children[child_index]
                    child = self.pager.read_page(child_page_num)
                    child.delete_cell(key)
                    self.pager.write_page(child_page_num, child)
        self.wal.clear()