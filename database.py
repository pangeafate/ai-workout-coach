import sqlite3

DB_NAME = "workout_coach.db"

def initialize_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_workout(date: str, exercise: str, details: str):
    """Insert a new workout entry into the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO workout_logs (date, exercise, details)
        VALUES (?, ?, ?)
    ''', (date, exercise, details))
    conn.commit()
    conn.close()

def get_all_workouts():
    """Retrieve all workout logs."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM workout_logs ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    initialize_db()
    print("Database initialized.")
