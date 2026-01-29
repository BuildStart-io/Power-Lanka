import sys
import sqlite3
import os

# Path to database
# Path to database
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend/data/rag_agent.db")

print(f"Migrating database at: {DB_PATH}")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'role' in columns:
            print("Column 'role' already exists. Skipping.")
        else:
            print("Adding 'role' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'admin'")
            conn.commit()
            print("Migration successful: Added 'role' column with default 'admin'.")
            
        # Verify content
        cursor.execute("SELECT email, role FROM users")
        users = cursor.fetchall()
        print("Current Users:", users)
            
    except Exception as e:
        print(f"Error during migration: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
