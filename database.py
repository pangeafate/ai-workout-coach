import sqlite3
import json

DB_NAME = "workout_coach.db"

def initialize_db():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create the users table to store user information.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create the workout_logs table with a user_id foreign key.
    c.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username):
    """Insert a new user into the database, or ignore if it exists.
       Returns the user id."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_users():
    """Retrieve a list of all users."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "username": row[1]} for row in rows]

def add_workout(date: str, user_id: int, workout_type: str, details: dict):
    """
    Insert a new workout entry into the database.
    
    Parameters:
      - date: The workout date (string).
      - user_id: The id of the user this workout belongs to.
      - workout_type: A string indicating the type (e.g., 'gym' or 'wod').
      - details: A dictionary containing workout-specific details.
    """
    details_json = json.dumps(details)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO workout_logs (date, user_id, workout_type, details)
        VALUES (?, ?, ?, ?)
    ''', (date, user_id, workout_type, details_json))
    conn.commit()
    conn.close()

def get_all_workouts():
    """Retrieve all workout logs and convert the details JSON back to a dictionary."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    c = conn.cursor()
    c.execute("SELECT * FROM workout_logs ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    
    workouts = []
    for row in rows:
        try:
            details = json.loads(row["details"]) if row["details"] else {}
        except Exception as e:
            details = {}
        workout = {
            "id": row["id"],
            "date": row["date"],
            "user_id": row["user_id"],
            "workout_type": row["workout_type"],
            "details": details
        }
        workouts.append(workout)
    return workouts

if __name__ == '__main__':
    initialize_db()
    print("Database initialized.")
