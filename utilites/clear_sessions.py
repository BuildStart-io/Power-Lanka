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
