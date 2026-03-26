import sqlite3
import os

DB_PATH = os.path.join('bot', 'KOKC.db')

def clear_bot_database():
    if not os.path.exists(DB_PATH):
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DELETE FROM manager_requests")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM clients")
    cursor.execute("DELETE FROM sqlite_sequence")
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()

clear_bot_database()
