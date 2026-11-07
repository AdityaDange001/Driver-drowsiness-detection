
import sqlite3
from datetime import datetime

# Create or open database
connection = sqlite3.connect("drowsiness.db")
cursor = connection.cursor()

# Create events table
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_time TEXT NOT NULL
)
""")

# Insert sample events
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.execute(
    "INSERT INTO events (event_type, event_time) VALUES (?, ?)",
    ("Drowsiness Warning", current_time)
)

cursor.execute(
    "INSERT INTO events (event_type, event_time) VALUES (?, ?)",
    ("Yawning Detected", current_time)
)

connection.commit()

# Display saved events
cursor.execute(
    "SELECT id, event_type, event_time FROM events ORDER BY id DESC"
)

print("\nSaved Events:")
for event in cursor.fetchall():
    print(event)

connection.close()

print("\nDatabase test successful!")
