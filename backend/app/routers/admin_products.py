from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import shutil
import os
from pathlib import Path
import json

from ..database import get_db, Product, get_sl_time

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

# Response Model
class ProductResponse(BaseModel):
    id: str
    product_name: str
    variant: Optional[str]
    price_lkr: float
    available: str
    image_paths: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)):
    """List all products in the catalog."""
    products = db.query(Product).order_by(Product.product_name.asc()).all()
    print(f"DEBUG: Returning {len(products)} products")
    return products

@router.post("/", response_model=ProductResponse)
async def create_or_update_product(
    id: Optional[str] = Form(None),
    product_name: str = Form(...),
    variant: Optional[str] = Form(""),
    price_lkr: float = Form(...),
    available: str = Form("Yes"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new product or update an existing one using Form Data."""
    p_name = product_name.strip()
    p_variant = variant.strip() if variant else ""
    
    # Generate ID if not provided and normalize to lowercase
    p_id = id if id else (f"{p_name}_{p_variant}" if p_variant else p_name)
    p_id = p_id.lower().replace(" ", "_") # Standardize format
    
    existing_product = db.query(Product).filter(Product.id == p_id).first()
    
    # Handle Image Upload
    final_image_path = None
    if image:
        # Create media directory if not exists
        media_dir = Path("media")
        media_dir.mkdir(exist_ok=True)
        
        # Save file
        file_extension = Path(image.filename).suffix
        filename = f"{p_id}_{int(get_sl_time().timestamp())}{file_extension}"
        file_path = media_dir / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # For now, we store just the filename or comma-separated list
        # If updating, we might want to append, but for simplicity let's replace or add to list
        final_image_path = filename

    if existing_product:
        existing_product.product_name = p_name
        existing_product.variant = p_variant
        existing_product.price_lkr = price_lkr
        existing_product.available = available
        existing_product.last_updated = get_sl_time()
        
        if final_image_path:
            # If there's an existing image, we could append it or replace
            # Let's append if not empty
            if existing_product.image_paths:
                existing_product.image_paths = f"{existing_product.image_paths},{final_image_path}"
            else:
                existing_product.image_paths = final_image_path
                
        db.commit()
        db.refresh(existing_product)
        return existing_product
    else:
        new_product = Product(
            id=p_id,
            product_name=p_name,
            variant=p_variant,
            price_lkr=price_lkr,
            available=available,
            image_paths=final_image_path,
            last_updated=get_sl_time()
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
    
    # Clean up images
    if product.image_paths:
        for img in product.image_paths.split(','):
            img = img.strip()
            if img:
                img_path = Path("media") / img
                if img_path.exists():
                    try:
                        os.remove(img_path)
                    except Exception as e:
                        print(f"Error deleting image {img}: {e}")

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
    product.last_updated = get_sl_time()
    db.commit()
    db.refresh(product)
    return {"id": product_id, "available": product.available}

@router.delete("/{product_id}/images/{filename}")
async def delete_product_image_endpoint(product_id: str, filename: str, db: Session = Depends(get_db)):
    """Delete a specific image from a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if not product.image_paths:
         raise HTTPException(status_code=404, detail="Image not found in product")
         
    # Filter out the image
    current_images = [img.strip() for img in product.image_paths.split(',') if img.strip()]
    if filename not in current_images:
        raise HTTPException(status_code=404, detail="Image not linked to this product")
        
    current_images.remove(filename)
    product.image_paths = ",".join(current_images)
    
    # Delete file
    img_path = Path("media") / filename
    if img_path.exists():
        try:
            os.remove(img_path)
        except Exception:
            pass # Ignore file system errors if file already gone
            
    db.commit()
    db.refresh(product)
    return {"message": "Image deleted", "image_paths": product.image_paths}
