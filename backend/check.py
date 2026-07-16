import sqlite3
c = sqlite3.connect('test.db')
print(c.execute("SELECT * FROM users;").fetchall())
