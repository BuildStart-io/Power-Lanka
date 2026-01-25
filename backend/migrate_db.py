
import sqlite3
import os
from pathlib import Path

# Path to database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "rag_agent.db"

def migrate():
    print(f"Checking database at: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("Database not found. It will be created when the app runs.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "image_paths" not in columns:
            print("Adding 'image_paths' column to 'products' table...")
            cursor.execute("ALTER TABLE products ADD COLUMN image_paths TEXT")
            conn.commit()
            print("Migration successful: Added 'image_paths'.")
        else:
            print("'image_paths' column already exists.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
