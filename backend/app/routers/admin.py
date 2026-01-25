from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db, User, Product

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
    # Count real data
    total_customers = db.query(User).count() # Using admins as customers for now, or use WhatsAppSessions
    # Actually, let's use WhatsApp sessions as "Customers"
    # total_customers = db.query(WhatsAppSession).count() 
    # But User model is imported. WhatsAppSession needs import if we use it.
    
    products_count = db.query(Product).count()
    
    return {
        "total_orders": 12, # Mock
        "pending_orders": 2, # Mock
        "total_revenue": 45000, # Mock
        "total_customers": total_customers,
        "total_items_sold": products_count * 5 # Mock
    }

@router.get("/product")
async def get_featured_product(db: Session = Depends(get_db)):
    """Get the featured product for the dashboard."""
    # Just return the first product or a dummy one
    product = db.query(Product).first()
    
    if not product:
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
        
    return {
        "product": {
            "name": product.product_name,
            "price": product.price_lkr,
            "name_si": product.variant or "", # Using variant as subtext for now
            "image_paths": "placeholder.png" # We need to handle images or add column
        },
        "delivery_charge": 350
    }

# We need imports for File upload
from fastapi import UploadFile, File
import shutil
import os

@router.post("/product/images")
async def upload_product_image(file: UploadFile = File(...)):
    """Upload a product image."""
    try:
        file_path = f"media/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/product/images/{filename}")
async def delete_product_image(filename: str):
    """Delete a product image."""
    try:
        file_path = f"media/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "Image deleted"}
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
