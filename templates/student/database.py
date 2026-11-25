
import sqlite3

def create_table():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            email TEXT,
            course TEXT
        )
    """)

    conn.commit()
    conn.close()

create_table()

print("Student Database Created Successfully!")
