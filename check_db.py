
import sqlite3

conn = sqlite3.connect("drowsiness.db")

result = conn.execute("PRAGMA integrity_check").fetchone()
print("Database:", result[0])

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type = ?",
    ("table",)
).fetchall()

print("Tables:", tables)

conn.close()

