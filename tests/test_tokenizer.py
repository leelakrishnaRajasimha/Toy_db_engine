"""
test_tokenizer.py

Verifies the tokenizer splits raw SQL text into the correct token sequence for each statement type
we plan to support.
"""

from tinydb_engine.sql.tokenizer import tokenize
tokens = tokenize("INSERT INTO users VALUES (1, 'sam')")
kinds = [t.kind for t in tokens]
values = [t.value for t in tokens]
print("Tokens:", tokens)
assert kinds == ["KEYWORD", "KEYWORD", "IDENT", "KEYWORD", "LPAREN", "NUMBER", "COMMA", "STRING", 
                 "RPAREN"]
assert values == ["INSERT", "INTO", "users", "VALUES", "(", "1", ",", "'sam'", ")"]
tokens2 = tokenize("SELECT * FROM users WHERE id = 5")
print("Tokens2:", tokens2)
assert [t.kind for t in tokens2] == ["KEYWORD", "STAR", "KEYWORD", "IDENT", "KEYWORD", "IDENT", 
                                      "EQ", "NUMBER"]
print("ALL TOKENIZER CHECKS PASSED")