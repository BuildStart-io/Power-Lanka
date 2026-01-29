
import sys
import os
import uuid

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, 'backend'))

from app.database.database import get_db, Product, Order, WhatsAppSession, ConversationMessage
from app.agent.tools import add_to_cart, view_cart, save_shipping_details, confirm_order, get_product_by_name

# Setup a test phone number
TEST_PHONE = "94770000000"

def setup_test_session():
    db = next(get_db())
    # Clear existing session for clean test
    existing = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == TEST_PHONE).first()
    if existing:
        # Delete related orders to avoid constraint issues if needed, or just delete session
        # For this test, we just ensure a session exists
        pass
    else:
        session = WhatsAppSession(
            id=str(uuid.uuid4()),
            phone_number=TEST_PHONE,
            session_id=str(uuid.uuid4())
        )
        db.add(session)
        db.commit()
    print(f"✅ Session ready for {TEST_PHONE}")

def test_fuzzy_search():
    print("\n--- Testing Product Search ---")
    queries = [
        "fly killer",
        "power fly",
        "deep clean",
        "odour",
        "neutralizer"
    ]
    
    for q in queries:
        p = get_product_by_name(q)
        if p:
            print(f"Query '{q}' -> Found: {p.product_name} ({p.variant})")
        else:
            print(f"Query '{q}' -> ❌ Not Found")

def test_order_flow():
    print("\n--- Testing Order Flow ---")
    
    # 1. Add to cart
    print("1. Adding 'fly killer' to cart...")
    res = add_to_cart(TEST_PHONE, "fly killer", 1)
    print(f"Result: {res}")
    
    print("2. Adding 'DeepClean' to cart...")
    res = add_to_cart(TEST_PHONE, "DeepClean", 2)
    print(f"Result: {res}")
    
    # 2. View Cart
    print("\n3. Viewing Cart...")
    res = view_cart(TEST_PHONE)
    print(f"Result:\n{res}")
    
    # 3. Save Details
    print("\n4. Saving Shipping Details...")
    res = save_shipping_details(TEST_PHONE, name="Test User", address="123 Test Lane", district="Colombo")
    print(f"Result: {res}")
    
    # 4. Confirm
    print("\n5. Confirming Order...")
    res = confirm_order(TEST_PHONE)
    print(f"Result: {res}")

if __name__ == "__main__":
    try:
        setup_test_session()
        test_fuzzy_search()
        test_order_flow()
        print("\n✅ Verification Complete")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
