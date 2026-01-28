from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db, User, Product, Order, OrderItem, WhatsAppSession
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

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
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
            "full_name": user.full_name
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
        full_name=user_data.full_name
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
        unique_filename = f"featured_{int(datetime.utcnow().timestamp())}{file_extension}"
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
    query = db.query(Order).order_by(Order.created_at.desc())
    
    if status:
        query = query.filter(Order.status == status)
        
    orders = query.all()
    
    # Format for frontend
    return {
        "orders": [
            {
                "id": o.id,
                "phone": o.session_id, # Using session ID as phone for now, ideally join with WhatsAppSession
                "customer_name": o.shipping_name or "Guest",
                "total_amount": o.total_amount,
                "item_count": len(o.items),
                "status": o.status,
                "created_at": o.created_at
            }
            for o in orders
        ]
    }

@router.get("/orders/{order_id}")
async def get_order_details(order_id: str, db: Session = Depends(get_db)):
    """Get full details for a specific order."""
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {
        "id": order.id,
        "phone": order.session_id,
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
    
    return {"message": "Status updated", "status": order.status}
