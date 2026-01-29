from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import csv
import io
from fastapi.responses import StreamingResponse

from ..database import get_db, User, Product, Order, OrderItem, WhatsAppSession, get_sl_time
from ..database.database import format_price

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/ping")
async def ping():
    return {"status": "ok"}

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[str] = "staff"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: Optional[str]
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Simple admin login - verifies email and password."""
    # In a real app, use bcrypt to check password_hash
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or user.password_hash != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Return a mock token and user info as expected by frontend
    return {
        "token": f"mock_token_{uuid.uuid4()}",
        "user": {
            "email": user.email,
            "name": user.full_name,
            "role": user.role or "admin"
        }
    }

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """List all admin users."""
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new admin user."""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=user_data.password, # For production, hash this
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete an admin user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting the last admin or the user themselves (optional but good)
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

class UserUpdatePassword(BaseModel):
    password: str

class UserUpdateRole(BaseModel):
    role: str

@router.put("/users/{user_id}/password")
async def update_user_password(
    user_id: str, 
    data: UserUpdatePassword,
    db: Session = Depends(get_db)
):
    """Reset a user's password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = data.password
    db.commit()
    return {"message": "Password updated successfully"}

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str, 
    data: UserUpdateRole,
    db: Session = Depends(get_db)
):
    """Update a user's role."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if data.role not in ["admin", "staff"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user.role = data.role
    db.commit()
    return {"message": "Role updated successfully"}

# --- Dashboard Stats & Product Endpoints ---

@router.get("/stats")
async def get_dashboard_stat(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    from sqlalchemy import func
    
    # Total Orders
    total_orders = db.query(Order).count()
    
    # Pending Orders (Assuming 'pending' is the status for new orders)
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    
    # Total Revenue
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    
    # Total Customers (Unique WhatsApp Sessions)
    total_customers = db.query(WhatsAppSession).count()
    
    # Total Items Sold
    total_items_sold = db.query(func.sum(OrderItem.quantity)).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_items_sold": total_items_sold
    }

@router.get("/product")
async def get_featured_product(db: Session = Depends(get_db)):
    """Get the featured product for the dashboard."""
    display_product = None
    
    # Try to find a logical "featured" product
    # Priority 1: A product with an image
    # Priority 2: Any product
    
    product_with_image = db.query(Product).filter(Product.image_paths != None, Product.image_paths != "").first()
    
    if product_with_image:
        display_product = product_with_image
    else:
        display_product = db.query(Product).first()
    
    if not display_product:
        # Return a placeholder if DB is empty
        return {
            "product": {
                "name": "No Product",
                "price": 0,
                "name_si": "",
                "image_paths": ""
            },
            "delivery_charge": 350
        }
    
    # Helper to get first image if comma separated
    images = display_product.image_paths if display_product.image_paths else ""
        
    return {
        "product": {
            "name": display_product.product_name,
            "price": display_product.price_lkr,
            "name_si": display_product.variant or "", 
            "image_paths": images 
        },
        "delivery_charge": 350
    }

@router.get("/products")
async def list_products(category_id: Optional[str] = None, db: Session = Depends(get_db)):
    """List all products, optionally filtered by category (not used yet)."""
    # In simple mode, we just return all products
    products = db.query(Product).all()
    
    return {
        "products": [
            {
                "id": p.id,
                "name": p.product_name,
                "variant": p.variant,
                "name_si": p.variant, # Mapping variant to name_si for existing frontend compat
                "price": p.price_lkr,
                "image_paths": p.image_paths,
                "is_active": True # Default to true
            }
            for p in products
        ]
    }

@router.get("/products/{product_id}")
async def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    """Get a specific product details including stock (mocked)."""
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return {
        "id": product.id,
        "name": product.product_name,
        "name_si": product.variant,
        "price": product.price_lkr,
        # Mock phone_stock for compatibility if needed, but we removed it from frontend
        "phone_stock": []
    }

# We need imports for File upload
from fastapi import UploadFile, File
import shutil
import os

@router.post("/product/images")
async def upload_product_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a product image and attach it to the featured product."""
    try:
        # Create media directory if not exists
        media_dir = Path("media")
        media_dir.mkdir(exist_ok=True)
        
        # Save file
        file_extension = Path(file.filename).suffix
        # Use timestamp to avoid collisions
        unique_filename = f"featured_{int(get_sl_time().timestamp())}{file_extension}"
        file_path = media_dir / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Find the product to attach to (same logic as get_featured_product)
        # Priority 1: A product with an image (likely the one we are viewing)
        # Priority 2: Any product (if adding first image)
        product = db.query(Product).filter(Product.image_paths != None, Product.image_paths != "").first()
        if not product:
            product = db.query(Product).first()
            
        if product:
            if product.image_paths:
                product.image_paths = f"{product.image_paths},{unique_filename}"
            else:
                product.image_paths = unique_filename
            db.commit()
            db.refresh(product)
            
        return {"filename": unique_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/product/images/{filename}")
async def delete_product_image(
    filename: str,
    db: Session = Depends(get_db)
):
    """Delete a product image and remove reference from DB."""
    try:
        # Remove from disk
        file_path = Path("media") / filename
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception:
                pass

        # Remove string reference from ANY product that has it
        # Since we don't have product_id, we search (inefficient but safe for small catalog)
        products = db.query(Product).filter(Product.image_paths.contains(filename)).all()
        
        for product in products:
            if not product.image_paths:
                continue
                
            current_paths = [p.strip() for p in product.image_paths.split(',') if p.strip()]
            if filename in current_paths:
                current_paths.remove(filename)
                product.image_paths = ",".join(current_paths)
                db.add(product) # Mark for update
                
        db.commit()
            
        return {"message": "Image deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- Order Management Endpoints ---

class OrderUpdate(BaseModel):
    status: str

@router.get("/orders")
async def list_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all orders with optional status filter."""
    query = db.query(Order, WhatsAppSession).join(WhatsAppSession, Order.session_id == WhatsAppSession.id).order_by(Order.created_at.desc())
    
    if status:
        query = query.filter(Order.status == status)
        
    results = query.all()
    
    # Format for frontend
    return {
        "orders": [
            {
                "id": o.id,
                # Use phone number from the joined session table
                "phone": s.phone_number, 
                "customer_name": o.shipping_name or "Guest",
                "total_amount": o.total_amount,
                "item_count": len(o.items),
                "status": o.status,
                "created_at": o.created_at
            }
            for o, s in results
        ]
    }

@router.get("/orders/{order_id}")
async def get_order_details(order_id: str, db: Session = Depends(get_db)):
    """Get full details for a specific order."""
    # Join with WhatsAppSession to get phone number
    result = db.query(Order, WhatsAppSession).join(WhatsAppSession, Order.session_id == WhatsAppSession.id).filter(Order.id == order_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order, session = result
        
    return {
        "id": order.id,
        "phone": session.phone_number, # Return actual phone number
        "customer_name": order.shipping_name,
        "delivery_address": order.shipping_address,
        "delivery_city": order.shipping_district,
        "payment_method": order.payment_method,
        "status": order.status,
        "created_at": order.created_at,
        "total_amount": order.total_amount,
        "items": [
            {
                "id": item.id,
                "category_name": item.product.product_name,
                "phone_model": item.product.variant, 
                "quantity": item.quantity,
                "unit_price": item.unit_price
            }
            for item in order.items
        ]
    }

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str, 
    status_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update order status."""
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = status_update.status
    db.commit()
    
class ManualOrderItem(BaseModel):
    product_id: str
    quantity: int
    # phone_model_id is no longer needed for general products

class ManualOrderCreate(BaseModel):
    phone: str
    customer_name: str
    delivery_address: str
    delivery_city: Optional[str] = None
    gender: Optional[str] = None
    items: List[ManualOrderItem]
    payment_method: str
    special_note: Optional[str] = None

@router.post("/orders/manual")
async def create_manual_order(
    order_data: ManualOrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new order manually from the admin panel."""
    try:
        # 1. Get or Create WhatsApp Session for the customer
        # Sanitize phone number (basic)
        phone = order_data.phone.strip()
        
        session = db.query(WhatsAppSession).filter(WhatsAppSession.phone_number == phone).first()
        if not session:
            session = WhatsAppSession(
                id=str(uuid.uuid4()),
                phone_number=phone,
                session_id=str(uuid.uuid4()), # Generate a dummy session ID
                created_at=get_sl_time(),
                last_message_at=get_sl_time()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
        # 2. Calculate Total & Prepare Items
        total_amount = 0
        order_items_db = []
        
        for item_data in order_data.items:
            product = db.query(Product).get(item_data.product_id)
            if not product:
                continue
                
            unit_price = product.price_lkr
            item_total = unit_price * item_data.quantity
            total_amount += item_total
            
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=None, # Will set after creating order
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                subtotal=item_total
            )
            order_items_db.append(order_item)

        # Add delivery charge (standard 350 for now, or could be dynamic)
        delivery_charge = 350
        total_amount += delivery_charge
        
        # 3. Create Order
        new_order = Order(
            id=str(uuid.uuid4()),
            session_id=session.id,
            status="confirmed", # Manual orders are usually confirmed immediately
            total_amount=total_amount,
            payment_method=order_data.payment_method,
            shipping_name=order_data.customer_name,
            shipping_address=order_data.delivery_address,
            shipping_district=order_data.delivery_city,
            created_at=get_sl_time(),
            updated_at=get_sl_time()
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        # 4. Attach Items
        for item in order_items_db:
            item.order_id = new_order.id
            db.add(item)
            
        db.commit()
        
        return {"message": "Order created successfully", "order": {"id": new_order.id}}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/export/csv")
async def export_orders_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export orders to CSV with filters."""
    # Build Query
    query = db.query(Order).join(WhatsAppSession, Order.session_id == WhatsAppSession.id)
    
    if status:
        query = query.filter(Order.status == status)
        
    if start_date:
        # Assuming YYYY-MM-DD format from frontend
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.created_at >= s_date)
        except ValueError:
            pass
            
    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d")
            # Add one day to include the end date fully
            e_date = e_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= e_date)
        except ValueError:
            pass

    # Order by newest first
    query = query.order_by(Order.created_at.desc())
    
    orders = query.all()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Order ID",
        "Date",
        "Status",
        "Customer Name",
        "Phone Number",
        "Delivery Address",
        "City/District",
        "Items Summary",
        "Item Count",
        "Total Amount (Rs)",
        "Payment Method"
    ])
    
    for order in orders:
        # Get phone number from joined session (although join not explicit in result here, we need to access via relationship if set up, or re-query)
        # In the query above we did a join but query(Order) only returns Order objects unless we ask for both.
        # Let's rely on lazy loading/relationship or specific query structure.
        # To be safe and efficient, let's fix the query to eager load or just fetch since it's lazy by default.
        # Order model has session_id, but maybe not a direct relationship configured to WhatsAppSession in the audit?
        # Let's check: Order model has 'session_id = Column(String, ForeignKey("whatsapp_sessions.id"))'
        # But DOES NOT seem to have a 'session' relationship defined in the code I saw earlier (lines 81-106 of database.py).
        # Wait, I checked database.py earlier. Line 120 has `order = relationship("Order", back_populates="items")`.
        # Line 87 is column. 
        # I did NOT see a relationship to WhatsAppSession in `Order` class.
        # So I need to query manually or relying on the previous pattern in `list_orders`.
        
        # Pattern in list_orders: query(Order, WhatsAppSession).join...
        # Let's stick to that pattern for safety.
        pass

    # Re-running query with correct tuple select to match list_orders pattern
    query = db.query(Order, WhatsAppSession).join(WhatsAppSession, Order.session_id == WhatsAppSession.id)
    
    if status:
        query = query.filter(Order.status == status)
    if start_date:
        try:
            s_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.created_at >= s_date)
        except ValueError: pass
    if end_date:
        try:
            e_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= e_date)
        except ValueError: pass
        
    query = query.order_by(Order.created_at.desc())
    results = query.all()
    
    for order, session in results:
        # Format Items
        items_list = []
        for item in order.items:
            # item.product lazy load
            p_name = item.product.product_name if item.product else "Unknown"
            p_var = f" ({item.product.variant})" if item.product and item.product.variant else ""
            items_list.append(f"{p_name}{p_var} x{item.quantity}")
        
        items_summary = " | ".join(items_list)
        
        writer.writerow([
            order.id,
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            order.status.upper(),
            order.shipping_name or "Guest",
            session.phone_number,
            order.shipping_address or "",
            order.shipping_district or "",
            items_summary,
            len(order.items),
            f"{order.total_amount:.2f}",
            order.payment_method or "COD"
        ])
        
    output.seek(0)
    
    filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
