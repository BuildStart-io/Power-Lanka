#!/usr/bin/env python3
"""
Utility script to clean WhatsApp sessions and chat history from the database.
This allows starting fresh without affecting products, orders, or documents.
"""
import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "rag_agent.db")

def clean_whatsapp_data():
    """Delete all WhatsApp sessions and conversation history."""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Count before deletion
        cursor.execute("SELECT COUNT(*) FROM whatsapp_sessions")
        sessions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversation_messages")
        messages_count = cursor.fetchone()[0]
        
        print(f"📊 Found: {sessions_count} sessions, {messages_count} messages")
        
        # Delete conversation messages first (references session_id)
        cursor.execute("DELETE FROM conversation_messages")
        print(f"🗑️  Deleted {messages_count} conversation messages")
        
        # Delete WhatsApp sessions
        cursor.execute("DELETE FROM whatsapp_sessions")
        print(f"🗑️  Deleted {sessions_count} WhatsApp sessions")
        
        conn.commit()
        print("\n✅ WhatsApp data cleaned successfully!")
        print("   Products, Orders, and Documents are untouched.")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  Power Lanka - Clean WhatsApp Sessions")
    print("=" * 50)
    clean_whatsapp_data()
