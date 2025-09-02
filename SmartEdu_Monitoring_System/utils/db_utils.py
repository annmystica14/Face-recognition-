# utils/db_utils.py
import sqlite3

DB_PATH = 'database/faces.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS people
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      section TEXT,
                      department TEXT)''')
    conn.commit()
    conn.close()

def add_profile(name, section, department):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people (name, section, department) VALUES (?, ?, ?)", (name, section, department))
    conn.commit()
    conn.close()

def update_profile(old_name, new_name, section, department):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE people SET name=?, section=?, department=? WHERE name=?", (new_name, section, department, old_name))
    conn.commit()
    conn.close()

def remove_profile(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE name=?", (name,))
    conn.commit()
    conn.close()

def get_profile(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, section, department FROM people WHERE name=?", (name,))
    profile = cursor.fetchone()
    conn.close()
    return profile

def fetch_profile(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, section, department FROM people WHERE name=?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "name": result[0],
            "section": result[1],
            "department": result[2]
        }
    return None

# Insert a new person into database
def insert_person(name, section, department):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO people (name, section, department) VALUES (?, ?, ?)",
                   (name, section, department))
    conn.commit()
    conn.close()

# Edit existing profile
def update_profile(old_name, new_name, section, department):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE people SET name=?, section=?, department=? WHERE name=?",
                   (new_name, section, department, old_name))
    conn.commit()
    conn.close()

# Delete a profile by name
def delete_profile(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM people WHERE name=?", (name,))
    conn.commit()
    conn.close()

# Get all names in database
def get_all_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM people")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names