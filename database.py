import sqlite3
from datetime import datetime

DB_NAME = "mental_health.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create tables if they don’t exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT,
            mood_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS removed_activities (
            activity TEXT PRIMARY KEY,
            cooldown INTEGER,
            date_removed TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure the "date_removed" column exists in removed_activities
    cursor.execute("PRAGMA table_info(removed_activities);")
    columns = [row[1] for row in cursor.fetchall()]

    if "date_removed" not in columns:
        cursor.execute("ALTER TABLE removed_activities ADD COLUMN date_removed TEXT DEFAULT CURRENT_TIMESTAMP")
        print("✅ Added 'date_removed' column to removed_activities.")

    # Create unique index for mood_feedback to avoid duplicate entries for the same day
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_activity_date ON mood_feedback(activity, DATE(timestamp));
    """)

    conn.commit()
    conn.close()


def get_last_recommendations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT activity FROM recommendations ORDER BY id DESC LIMIT 5")
    results = cursor.fetchall()
    
    conn.close()
    
    return [row[0] for row in results]

def save_recommendations(activities):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM recommendations")  # Clear previous recommendations
    for activity in activities:
        cursor.execute("INSERT INTO recommendations (activity) VALUES (?)", (activity,))
    
    conn.commit()
    conn.close()

def save_mood_feedback(activity, mood_score):
    conn = sqlite3.connect("mental_health.db")
    cursor = conn.cursor()

    # Use the ON CONFLICT clause to handle updates without needing a DELETE
    cursor.execute("""
        INSERT INTO mood_feedback (activity, mood_score, timestamp)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(activity, DATE(timestamp)) DO UPDATE SET
        mood_score = excluded.mood_score,
        timestamp = datetime('now')
    """, (activity, mood_score))

    conn.commit()
    conn.close()
    print(f"✅ Feedback for '{activity}' saved successfully!")


def get_mood_feedback():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT activity, AVG(mood_score) FROM mood_feedback GROUP BY activity")
    results = cursor.fetchall()
    
    conn.close()
    
    return {row[0]: row[1] for row in results}  # Returns average mood score per activity

def get_removed_activities():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT activity, cooldown FROM removed_activities")
    results = cursor.fetchall()
    
    conn.close()
    
    return {row[0]: row[1] for row in results}  # Return dictionary of removed activities

def save_removed_activities(removed_activities):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM removed_activities")  # Clear previous removed activities
    for activity, cooldown in removed_activities.items():
        cursor.execute("INSERT INTO removed_activities (activity, cooldown) VALUES (?, ?)", (activity, cooldown))
    
    conn.commit()
    conn.close()

def reset_old_removed_activities():
    """Reset activities back to neutral (5) if 1 minute has passed since removal."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ensure the date_removed column exists
    cursor.execute("PRAGMA table_info(removed_activities);")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "date_removed" not in columns:
        print("❌ 'date_removed' column missing in removed_activities! Ensure schema is correct.")
        conn.close()
        return

    # Find activities that were removed more than 1 minute ago
    cursor.execute("""
        SELECT activity FROM removed_activities
        WHERE datetime(date_removed) <= datetime('now', '-1 minute')
    """)
    old_activities = cursor.fetchall()

    for (activity,) in old_activities:
        print(f"🔄 Restoring {activity} to neutral (5)...")

        # Update mood score to 5 in mood_feedback
        cursor.execute("""
            UPDATE mood_feedback
            SET mood_score = 5, timestamp = ?
            WHERE activity = ?
        """, (datetime.now().isoformat(), activity))

        # Remove from removed_activities
        cursor.execute("""
            DELETE FROM removed_activities WHERE activity = ?
        """, (activity,))

    conn.commit()
    conn.close()

# Initialize DB on first run
init_db()
