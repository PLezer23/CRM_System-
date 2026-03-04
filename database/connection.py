import sqlite3
from datetime import datetime
import os



class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.db_path = os.path.join(project_root, 'bot', 'KOKC.db')
        else:
            self.db_path = db_path

        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES clients (user_id)
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS manager_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES clients (user_id)
                )
            ''')

            conn.commit()

    def save_or_update_user(self, user_id, username, first_name, last_name=None):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO clients 
                (user_id, username, first_name, last_name, last_seen)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            conn.commit()

    def save_message(self, user_id, message, response):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO messages (user_id, message, response)
                VALUES (?, ?, ?)
            ''', (user_id, message, response))
            conn.commit()

    def save_manager_request(self, user_id, message):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO manager_requests (user_id, message, status)
                VALUES (?, ?, 'pending')
            ''', (user_id, message))
            conn.commit()
