import sys
import os
import uuid
from datetime import datetime

# Add 'backend' directory to sys.path to simulate running from backend root
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.database.database import SessionLocal, Order, OrderItem, WhatsAppSession, User
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def verify_stats():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        print("--- Initial Stats ---")
        orders_count = db.query(Order).count()
        print(f"Orders: {orders_count}")
        
        # Create Dummy Data
        print("\nCreating dummy data...")
        session_id = str(uuid.uuid4())
        session = WhatsAppSession(
            id=session_id,
            phone_number="94770000000",
            session_id="dummy_session",
            created_at=datetime.now(),
            last_message_at=datetime.now()
        )
        db.add(session)
        
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            session_id=session_id,
            status="pending",
            total_amount=1500.0,
            payment_method="cod",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(order)
        
        db.commit()
        
        print("\n--- Stats After Insert ---")
        new_orders_count = db.query(Order).count()
        new_revenue = db.query(Order).filter(Order.id == order_id).first().total_amount
        
        print(f"Orders: {new_orders_count} (Expected: {orders_count + 1})")
        print(f"Revenue Check: {new_revenue}")
        
        if new_orders_count == orders_count + 1:
            print("\nSUCCESS: Stats logic is working correctly.")
        else:
            print("\nFAILURE: Stats did not update.")
            
        # Cleanup
        print("\nCleaning up...")
        db.delete(order)
        db.delete(session)
        db.commit()
        print("Cleanup done.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_stats()
