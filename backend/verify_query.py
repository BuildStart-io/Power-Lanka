import sys
import os

# Add backend directory to path
sys.path.append('/home/lord/Projects/Power-Lanka-Project/PL_Server/backend')

from app.database import get_db, Order, WhatsAppSession

def test_query():
    db = next(get_db())
    try:
        print("Testing Order + WhatsAppSession Join Query...")
        query = db.query(Order, WhatsAppSession).join(WhatsAppSession, Order.session_id == WhatsAppSession.id).order_by(Order.created_at.desc())
        # Just try to compile/execute without fetching all data if massive, but limit 1 is fine
        results = query.limit(1).all()
        print("Query executed successfully!")
        print(f"Found {len(results)} results (limit 1)")
        if results:
            o, s = results[0]
            print(f"Sample - Order ID: {o.id}, Phone: {s.phone_number}")
    except Exception as e:
        print(f"Query Failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
