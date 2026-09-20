"""
test_parser.py

Verifies the parser turn tokenized SQL into the correct AST node for each of the four statement 
types.

"""

from tinydb_engine.sql.parser import parse_sql
create = parse_sql("CREATE TABLE users(id, name)")
print("CREATE:", create)
assert create.table_name == "users"
assert create.columns == ["id", "name"]
insert = parse_sql("INSERT INTO users VALUES (1, 'raj')")
print("INSERT:", insert)
assert insert.table_name == "users"
assert insert.values == [1, 'raj']
select_all = parse_sql("SELECT * FROM users")
print("Select(no WHERE):", select_all)
assert select_all.table_name == "users"
assert select_all.where_column is None
select_where = parse_sql("SELECT * FROM users WHERE id = 1")
print("Select(WHERE):", select_where)
assert select_where.where_column == "id"
assert select_where.where_value == 1
delete = parse_sql("DELETE FROM users WHERE id = 1")
print("DELETE:", delete)
assert delete.table_name == "users"
assert delete.where_column == "id"
assert delete.where_value == 1
print("ALL PARSER CHECKS PASSED")