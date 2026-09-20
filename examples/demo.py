"""
demo.py

Minimal demonstartion of the engines public API. Run this from the project root with:
python -m examples.demo
"""

from tinydb_engine.engine import Engine
with Engine("data/demo.db") as db:
    db.execute("CREATE TABLE users (id, name)")
    db.execute("INSERT INTO users VALUES (1, 'raj')")
    db.execute("INSERT INTO users VALUES (2, 'sam')")
    result = db.execute("SELECT * FROM users WHERE id = 1")
    print("User 1:", result)
    db.execute("DELETE FROM users WHERE id = 2")
    print("User2 after delete:", db.execute("SELECT * FROM users WHERE id = 2"))
print("Demo complete check data/demo.db and data/demo.wal on disk.")