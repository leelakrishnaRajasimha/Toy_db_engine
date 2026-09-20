"""
page.py

One page = one fixed size slab of the database file(4096 bytes, matching common OS page/disk_sector
sizes this is why databases use this number, not an arbitrary choice).

Anatomy of a page on disk:
    Header   - Cells(key, value pairs).
    16 bytes - up to PAGE_SIZE - 16 bytes.
    
Header (16 bytes total):
    Page type : 1 byte - 1 = Leaf, 2 = Internal(splitting comes later).
    num_cells : 2 bytes - How many cells to expect when parsing.
    reserved  : 13 bytes - Unused for now, future home for a right sibling pointer, checksum, etc.
                           Reserving it now means the on disk format doesn't shift later.

"""

import struct
PAGE_SIZE = 4096
HEADER_SIZE = 16

PAGE_TYPE_LEAF = 1
PAGE_TYPE_INTERNAL = 2

HEADER_FORMAT = ">BH13x"

class Page:
    def __init__(self, page_type: int = PAGE_TYPE_LEAF):
        self.page_type = page_type
        self.cells: list[tuple[bytes, bytes]] = []
        self.children: list[int] = []

    def is_leaf(self) -> bool:
        return self.page_type == PAGE_TYPE_LEAF

    def insert_cell(self, key: bytes, value: bytes) -> None:
        for i, (existing_key, _) in enumerate(self.cells):
            if existing_key == key:
                self.cells[i] = (key, value)
                return
            if existing_key > key:
                self.cells.insert(i, (key, value))
                return
        self.cells.append((key, value))

    def find_cell(self, key: bytes) -> bytes | None:
        for existing_key, value in self.cells:
            if existing_key == key:
                return value
        return None
    
    def delete_cell(self, key: bytes) -> bool:
        for i, (existing_key, _) in enumerate(self.cells):
            if existing_key == key:
                del self.cells[i]
                return True
        return False
    
    def used_bytes(self) -> int:
        return sum(4 + len(k) + len(v) for k, v in self.cells)
    
    def is_full(self) -> bool:
        return self.used_bytes() > PAGE_SIZE - HEADER_SIZE - 64
    
    def to_bytes(self) -> bytes:
        header = struct.pack(HEADER_FORMAT, self.page_type, len(self.cells))

        body = bytearray()
        for key, value in self.cells:
            body += struct.pack(">HH", len(key), len(value))
            body += key
            body += value
        if len(header) + len(body) > PAGE_SIZE:
            raise ValueError("Page overflow: Too much data for one page")
        padding = b"\x00" * (PAGE_SIZE - len(header) - len(body))
        return header + bytes(body) + padding
    
    @classmethod
    def from_bytes(cls, raw: bytes) -> "Page":
        if len(raw) != PAGE_SIZE:
            raise ValueError(f"Expected {PAGE_SIZE} bytes, got {len(raw)}")
        page_type, num_cells = struct.unpack(HEADER_FORMAT, raw[:HEADER_SIZE])
        page = cls(page_type=page_type)
        offset = HEADER_SIZE
        for _ in range(num_cells):
            key_len, value_len = struct.unpack(">HH", raw[offset:offset + 4])
            offset += 4
            key = raw[offset:offset + key_len]
            offset += key_len
            value = raw[offset:offset + value_len]
            offset += value_len
            page.cells.append((key, value))
        return page
    
    def __repr__(self) -> str:
        kind = "leaf" if self.page_type == PAGE_TYPE_LEAF else "internal"
        return f"<Page type={kind} cells={len(self.cells)}>"