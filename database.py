import sqlite3
import json

DB_NAME = "workout_coach.db"

def initialize_db():
    """Creates the database and table if they don't exist with the new schema."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            workout_type TEXT NOT NULL,  -- e.g., 'gym' or 'wod'
            details TEXT                -- JSON string containing workout-specific information
        )
    ''')
    conn.commit()
    conn.close()

def add_workout(date: str, workout_type: str, details: dict):
    """
    Insert a new workout entry into the database.
    
    Parameters:
      - date: The workout date as a string (e.g., "2025-02-08").
      - workout_type: A string representing the type of workout ('gym' or 'wod').
      - details: A dictionary containing workout-specific details.
                 For gym workouts, this might include keys like "muscle_group", "exercise", "weight", "sets", "reps".
                 For WOD workouts, keys might include "block", "exercises", "time", "feedback".
    """
    details_json = json.dumps(details)  # Convert the details dictionary to a JSON string
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO workout_logs (date, workout_type, details)
        VALUES (?, ?, ?)
    ''', (date, workout_type, details_json))
    conn.commit()
    conn.close()

def get_all_workouts():
    """Retrieve all workout logs and convert the details JSON back to a dictionary."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM workout_logs ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    
    workouts = []
    for row in rows:
        try:
            details = json.loads(row[3])
        except Exception as e:
            details = {}
        workouts.append({
            "id": row[0],
            "date": row[1],
            "workout_type": row[2],
            "details": details
        })
    return workouts

if __name__ == '__main__':
    initialize_db()
    print("Database initialized.")
