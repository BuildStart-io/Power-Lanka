
import sqlite3
import os

DB_PATH = "data/rag_agent.db"

def check_db():
    print(f"Checking DB at: {os.path.abspath(DB_PATH)}")
    if not os.path.exists(DB_PATH):
        print("DB File does not exist!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        
        # Check products
        if ('products',) in tables:
            cursor.execute("SELECT id, product_name, image_paths FROM products")
            rows = cursor.fetchall()
            print(f"Product Count: {len(rows)}")
            for row in rows:
                print(row)
        else:
            print("Products table not found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
