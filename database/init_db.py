"""Database Initialization Script for EventEase.
Creates tables from schema.sql and seeds demo data.
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from database.seed_data import seed_database


def init_db(db_path=None, seed=True):
    """Initializes the SQLite database with tables and initial seed data."""
    target_path = Path(db_path) if db_path else Config.DATABASE
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    schema_path = BASE_DIR / "database" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
    print(f"[*] Initializing database at: {target_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("[+] Schema created successfully.")

    if seed:
        seed_database(target_path)


if __name__ == "__main__":
    should_seed = "--no-seed" not in sys.argv
    init_db(seed=should_seed)
