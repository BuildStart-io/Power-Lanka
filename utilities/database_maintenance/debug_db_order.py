import sys
import os

# Add project root to path
# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import get_db, WhatsAppSession, create_order, confirm_order_db, get_pending_order

def test_order_flow():
    print("--- Starting Order Flow Test ---")
    
    # 1. Setup Mock Session
    mock_phone = "94770000000"
    print(f"1. Using Mock Phone: {mock_phone}")
    
    db = next(get_db())
    
    # Ensure session exists (mocking what message handler does)
    # Ensure session exists (mocking what message handler does)
    from app.database.database import WhatsAppSession
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == mock_phone).first()
    if not session:
        print("Creating new session...")
        session = WhatsAppSession(id="test_session_id", phone_number=mock_phone, session_id="test_session_id")
        db.add(session)
        db.commit()
    
    print(f"Session found: {session.id}")
    
    # 2. Create Pending Order
    print("2. Creating Pending Order...")
    order = get_pending_order(db, session.id)
    if not order:
        order = create_order(db, session.id)
    print(f"Pending Order ID: {order.id}, Status: {order.status}")
    
    # 3. Add Item (Mock)
    # 3. Add Item (Mock)
    from app.database.database import add_order_item
    # Need a product ID
    # Need a product ID
    from app.database.database import Product
    product = db.query(Product).first()
    if not product:
        print("❌ No products found! Cannot test order item.")
        return
        
    print(f"Adding item: {product.product_name}")
    add_order_item(db, order.id, product.id, 1, 1500.0)
    
    # 4. Confirm Order (The Step Failing)
    print("4. Attempting Confirmation...")
    confirmed_order = confirm_order_db(
        db, 
        order.id, 
        name="Test User", 
        address="123 Test Lane", 
        district="Colombo", 
        payment="Bank Transfer"
    )
    
    if confirmed_order and confirmed_order.status == "confirmed":
        print(f"✅ SUCCESS: Order {confirmed_order.id} status is now '{confirmed_order.status}'")
    else:
        print(f"❌ FAILURE: Order status is {confirmed_order.status if confirmed_order else 'None'}")

if __name__ == "__main__":
    test_order_flow()
