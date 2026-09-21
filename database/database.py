import sqlite3

RACE_DB_FILE = "race_cache.db"
LOCATION_DB_FILE = "location_cache.db"


def init_db(db_type: str):
	"""Initializes a simple SQLite table to store race or location data."""
	if db_type == "race":
		db_file = RACE_DB_FILE
	elif db_type == "location":
		db_file = LOCATION_DB_FILE
	else:
		raise ValueError(f"Unsupported DB type '{db_type}")

	table_name = db_file.split(".")[0]
	conn = sqlite3.connect(db_file)
	cursor = conn.cursor()
	cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location INTEGER,
            url TEXT PRIMARY KEY,
            html TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
	conn.commit()
	conn.close()
