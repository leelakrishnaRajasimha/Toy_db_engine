"""
pager.py

This pager is the sole owner of the database file on the disk. Nothing above this layer not the 
B-tree, not the SQL layer is allowed to touch file offsets directly. Everything speaks in page
numbers.
This single rule is which makes the rest of the engine possible the B-tree can reason about "page X"
without knowing or caring that page X lives at byte 28,672 in the file. If we ever change PAGE_SIZE
then only this file needs to know.
"""

import os
from .page import PAGE_SIZE, Page
class Pager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        already_exists = os.path.exists(filepath)
        if not already_exists:
            open(filepath, "wb").close()
        self.file = open(filepath, "r+b")
        self.num_pages = os.path.getsize(filepath) // PAGE_SIZE if already_exists else 0

    def read_page(self, page_num: int) -> Page:
        if page_num >= self.num_pages:
            raise ValueError(f"page {page_num} does not exist (file has {self.num_pages})")
        self.file.seek(page_num * PAGE_SIZE)
        raw = self.file.read(PAGE_SIZE)
        if len(raw) != PAGE_SIZE:
            raise IOError(f"Short read on page {page_num}: got {len(raw)} bytes")
        return Page.from_bytes(raw)

    def write_page(self, page_num: int, page: Page) -> None:
        self.file.seek(page_num * PAGE_SIZE)
        self.file.write(page.to_bytes())
        self.file.flush()
        os.fsync(self.file.fileno())
        self.num_pages = max(self.num_pages, page_num + 1)

    def allocate_page(self, page: Page) -> int:
        new_page_num = self.num_pages
        self.write_page(new_page_num, page)
        return new_page_num

    def close(self):
        self.file.close()

    def __repr__(self) -> str:
        return f"<Pager file = {self.filepath!r} num_pages = {self.num_pages}>"