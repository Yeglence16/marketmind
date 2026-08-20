import sqlite3

DB_PATH = "alarms.db"    # created next to the process working directory


def init_db():
    """Create the alarms table if it does not exist. Safe to call on every startup."""
    conn = sqlite3.connect(DB_PATH) 
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stock TEXT NOT NULL,
            set_value REAL NOT NULL,
            direction TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



def add_alarm(user_id: int, stock: str, set_value: float, direction: str):
    """Store a new alarm. `direction` is decided at creation time, never asked from the user."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO alarms (user_id, stock, set_value, direction) VALUES (?, ?, ?, ?)",
        (user_id, stock, set_value, direction)
    )
    conn.commit()
    conn.close()


def get_user_alarms(user_id: int) -> list:
    """Alarms of one user, for display. Rows: (id, stock, set_value, direction) — no user_id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, stock, set_value, direction FROM alarms WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_alarms() -> list:
    """Every alarm, for the background checker. Rows include user_id so the DM can be sent."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, user_id, stock, set_value, direction FROM alarms"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_alarm(alarm_id: int, user_id: int) -> bool:
    """Delete one alarm. The user_id in the WHERE clause stops users deleting each other's alarms.

    Returns False if nothing matched.
    """    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "DELETE FROM alarms WHERE id = ? AND user_id = ?",
        (alarm_id, user_id)
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


if __name__ == "__main__":
    init_db()
    print("alarms.db hazır ✅")