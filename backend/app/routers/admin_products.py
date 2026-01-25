from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_db, Product

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

class ProductSchema(BaseModel):
    id: Optional[str] = None
    product_name: str
    variant: Optional[str] = ""
    price_lkr: float
    available: str = "Yes"

class ProductResponse(BaseModel):
    id: str
    product_name: str
    variant: Optional[str]
    price_lkr: float
    available: str
    last_updated: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)):
    """List all products in the catalog."""
    return db.query(Product).order_by(Product.product_name.asc()).all()

@router.post("/", response_model=ProductResponse)
async def create_or_update_product(product_data: ProductSchema, db: Session = Depends(get_db)):
    """Create a new product or update an existing one."""
    p_name = product_data.product_name.strip()
    p_variant = product_data.variant.strip() if product_data.variant else ""
    
    # Generate ID if not provided and normalize to lowercase
    p_id = product_data.id if product_data.id else (f"{p_name}_{p_variant}" if p_variant else p_name)
    p_id = p_id.lower().replace(" ", "_") # Standardize format
    
    existing_product = db.query(Product).filter(Product.id == p_id).first()
    
    if existing_product:
        existing_product.product_name = p_name
        existing_product.variant = p_variant
        existing_product.price_lkr = product_data.price_lkr
        existing_product.available = product_data.available
        existing_product.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(existing_product)
        return existing_product
    else:
        new_product = Product(
            id=p_id,
            product_name=p_name,
            variant=p_variant,
            price_lkr=product_data.price_lkr,
            available=product_data.available,
            last_updated=datetime.utcnow()
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

@router.delete("/{product_id}")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Delete a product from the database."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully", "id": product_id}

@router.patch("/{product_id}/availability")
async def toggle_availability(product_id: str, db: Session = Depends(get_db)):
    """Toggle product availability between 'Yes' and 'No'."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.available = "No" if product.available == "Yes" else "Yes"
    product.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return {"id": product_id, "available": product.available}
