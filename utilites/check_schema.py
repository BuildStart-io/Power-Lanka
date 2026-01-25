import sqlite3

def check_schema():
    conn = sqlite3.connect("data/rag_agent.db")
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables found:", [t[0] for t in tables])
    
    for table_name in tables:
        t = table_name[0]
        print(f"\nSchema for '{t}':")
        cursor.execute(f"PRAGMA table_info({t})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

    conn.close()

if __name__ == "__main__":
    check_schema()
