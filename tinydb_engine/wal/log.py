"""
log.py

The Write Ahead Log(WAL). Before any change touches a real data page it gets appended here first
and fsynced. That ordering is the entire point if we crash between 'logged it' and 'applied it to
the page' the log still has the record and replaying it on restart brings the data page back in 
sync. If we crash before it is logged the operation simply never happened which is the corect and
safe outcome.
On disk entry format one after another no delimiters needed because every field is length prefixed.

"""

import os
import struct

OP_INSERT = 1
OP_DELETE = 2

class WriteAheadLog:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = open(filepath, "ab")

    def log_insert(self, key: bytes, value: bytes) -> None:
        self._append(OP_INSERT, key, value)

    def log_delete(self, key: bytes) -> None:
        self._append(OP_DELETE, key, b"")

    def _append(self, op: int, key: bytes, value: bytes) -> None:
        entry = struct.pack(">B", op)
        entry += struct.pack(">H", len(key)) + key
        entry += struct.pack(">H", len(value)) + value
        self.file.write(entry)
        self.file.flush()
        os.fsync(self.file.fileno())

    def replay(self):
        with open(self.filepath, "rb") as f:
            while True:
                op_byte = f.read(1)
                if not op_byte:
                    break
                op = struct.unpack(">B", op_byte)[0]
                key_len = struct.unpack(">H", f.read(2))[0]
                key = f.read(key_len)
                value_len = struct.unpack(">H", f.read(2))[0]
                value = f.read(value_len) if value_len else b""
                yield (op, key, value)

    def close(self) -> None:
        self.file.close()

    def clear(self) -> None:
        self.file.close()
        self.file = open(self.filepath, "wb")
        self.file.close()
        self.file = open(self.filepath, "ab")