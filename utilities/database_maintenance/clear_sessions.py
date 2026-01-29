import sys
import os

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import SessionLocal, WhatsAppSession, ConversationMessage
from sqlalchemy import text

def clear_db():
    db = SessionLocal()
    try:
        print("Clearing whatsapp_sessions...")
        db.query(WhatsAppSession).delete()
        print("Clearing conversation_messages...")
        db.query(ConversationMessage).delete()
        db.commit()
        print("✅ Database cleared successfully.")
    except Exception as e:
        print(f"❌ Error clearing DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_db()
