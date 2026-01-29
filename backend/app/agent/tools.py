
from typing import List, Optional
import json
from ..database.database import (
    get_db, 
    Product, 
    Order, 
    OrderItem, 
    WhatsAppSession,
    get_or_create_customer,
    create_order,
    get_pending_order,
    add_order_item,
    confirm_order_db,
    format_price
)

# We will need the database session helper
# Ideally, tools should be independent or have a way to get a fresh session
# For simplicity in this agent framework, we'll use a direct DB helper pattern adapted for tools

def get_product_by_name(query: str) -> Optional[Product]:
    """Improved fuzzy search for product using word matching."""
    db = next(get_db())
    products = db.query(Product).filter(Product.available == "Yes").all()
    
    # Normalize query: lowercase, split into words, remove common words
    query_lower = query.lower()
    query_words = set(query_lower.replace("spray", "").replace("bottle", "").split())
    
    best_match = None
    best_score = 0
    
    for p in products:
        product_name_lower = p.product_name.lower()
        variant_lower = (p.variant or "").lower()
        
        # Score 1: Exact substring match in product name
        if query_lower in product_name_lower:
            return p
            
        # Score 1.5: Match neglecting spaces (e.g. "deep clean" matches "deepclean")
        if query_lower.replace(" ", "") in product_name_lower.replace(" ", ""):
            return p

        # Score 2: Word intersection matching
        product_words = set(product_name_lower.split())
        variant_words = set(variant_lower.split())
        all_product_words = product_words | variant_words
        
        # Count matching words
        matching_words = query_words & all_product_words
        score = len(matching_words)
        
        # Bonus for variant match (e.g., "4L" matches "4L Refill")
        if any(v in query_lower for v in variant_lower.split()):
            score += 2
            
        if score > best_score:
            best_score = score
            best_match = p
    
    # Require at least 1 significant word match
    if best_score >= 1:
        return best_match
        
    return None

def add_to_cart(phone: str, product_query: str, quantity: int = 1) -> str:
    """
    Finds a product and adds it to the user's cart.
    Arg: product_query (e.g. "Fly Spray", "DeepCleaner")
    """
    if quantity < 1:
        return "❌ Quantity must be at least 1."

    # 1. Identify Product
    product = get_product_by_name(product_query)
    if not product:
        # Get list of available products to show user
        db = next(get_db())
        all_products = db.query(Product).filter(Product.available == "Yes").all()
        product_list = "\n".join([f"- {p.product_name} ({p.variant})" for p in all_products])
        return f"❌ I couldn't find '{product_query}'.\n\nAvailable Products:\n{product_list}"

    # 2. Get/Create Order
    db = next(get_db())
    # Find session by phone
    # Note: In real production code we should handle 'not found' better 
    # but here we assume the message handler ensures session exists
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session:
        return "❌ Error: Session not found. Please type 'Hi' to start."
        
    order = get_pending_order(db, session.id)
    if not order:
        order = create_order(db, session.id)

    # 3. Add Item
    add_order_item(db, order.id, product.id, quantity, product.price_lkr)
    
    return f"✅ Added {quantity} x {product.product_name} ({product.variant}) to cart.\nTotal: {format_price(order.total_amount)}"

def view_cart(phone: str) -> str:
    """Shows the current items in the cart."""
    db = next(get_db())
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session: 
        return "No session found."
        
    order = get_pending_order(db, session.id)
    if not order or not order.items:
        return "🛒 Your cart is empty."
        
    response = ["🛒 *Your Cart*"]
    for item in order.items:
        # item.product might be lazy loaded, ensure mapped
        response.append(f"- {item.product.product_name} ({item.product.variant}) x{item.quantity}: {format_price(item.subtotal)}")
    
    response.append(f"\n💰 **Total: {format_price(order.total_amount)}**")
    response.append("\nType *'Checkout'* to verify your address.")
    return "\n".join(response)

def save_shipping_details(phone: str, name: str = None, address: str = None, district: str = None) -> str:
    """
    Saves shipping details to the pending order.
    Accepts partial updates (e.g. just name).
    """
    db = next(get_db())
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session:
        return "❌ Session not found. Please type 'Hi' to start."
    order = get_pending_order(db, session.id)
    
    if not order:
        return "❌ No active cart to save details for."

    saved_fields = []
    if name:
        order.shipping_name = name
        saved_fields.append("Name")
    if address:
        order.shipping_address = address
        saved_fields.append("Address")
    if district:
        order.shipping_district = district
        saved_fields.append("District")
    
    db.commit()
    
    # Check what is missing
    missing = []
    if not order.shipping_name: missing.append("Name")
    if not order.shipping_address: missing.append("Address")
    if not order.shipping_district: missing.append("District")
    
    if not missing:
        return f"✅ Saved {', '.join(saved_fields)}.\n\nReady to Confirm?\nName: {order.shipping_name}\nAddr: {order.shipping_address}\nDist: {order.shipping_district}\nTotal: {format_price(order.total_amount)}"
    else:
        return f"✅ Saved {', '.join(saved_fields)}.\n\nI still need your: {', '.join(missing)}."

def confirm_order(phone: str, payment_method: str = "COD") -> str:
    """
    Finalizes the order. Call this ONLY after details are collected.
    """
    db = next(get_db())
    session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
    if not session:
        return "❌ Session not found. Please type 'Hi' to start."
    order = get_pending_order(db, session.id)
    
    if not order:
        return "❌ No active order to confirm."

    # Validate details again
    if not (order.shipping_name and order.shipping_address and order.shipping_district):
        return "❌ Missing shipping details. Please provide Name, Address, and District."

    # Confirm
    confirm_order_db(db, order.id, order.shipping_name, order.shipping_address, order.shipping_district, payment_method)
    
    # In a real app, send WhatsApp notification, Email admin etc.
    
    return f"🎉 Order #{order.id[:8]} Confirmed!\n\n📦 We will ship to:\n{order.shipping_name}\n{order.shipping_address}\n{order.shipping_district}\n\n💰 Total: {format_price(order.total_amount)}\nPayment: {payment_method}"
