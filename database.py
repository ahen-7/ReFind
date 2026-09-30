
import sqlite3

DATABASE = "refind.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                color TEXT,
                location TEXT,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)



def add_item(report_type, name, category, color,
             location, description, image_path=None):

    if report_type not in ("Lost", "Found"):
        raise ValueError("Invalid report type")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO items (
                report_type, name, category,
                color, location, description, image_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_type,
            name,
            category,
            color,
            location,
            description,
            image_path
        ))

        return cursor.lastrowid

def get_items(report_type=None):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row

        if report_type:
            cursor = conn.execute(
                """SELECT * FROM items
                   WHERE report_type = ?
                   ORDER BY id DESC""",
                (report_type,)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM items ORDER BY id DESC"
            )

        return [dict(row) for row in cursor.fetchall()]
    
def add_image_column():
    with get_connection() as conn:
        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(items)"
            ).fetchall()
        ]

        if "image_path" not in columns:
            conn.execute(
                "ALTER TABLE items ADD COLUMN image_path TEXT"
            )