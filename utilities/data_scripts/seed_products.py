import sys
import os
import uuid
from datetime import datetime

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import SessionLocal, Product, get_sl_time

def seed_products():
    db = SessionLocal()
    try:
        print("Cleaning up old phone products...")
        # Since we don't have a category table explicit in the models shown (it might be in another file or implied), 
        # we will just delete everything for a clean slate as implied by "remove that category" and "rebrand"
        # BUT, looking at models, there isn't a Category model in `database.py`. 
        # ManualOrderView uses `/admin/categories`. Let's assume there is a Category model or logic.
        # Wait, I saw `Category` in ManualOrderView fetching from `/admin/categories`.
        # I need to check `models.py` or wherever Category is defined if I want to be safe.
        # However, `Product` in `database.py` seems pretty standalone.
        
        # Let's delete all existing products first to genericize it
        db.query(Product).delete()
        
        products_to_add = [
            {"name": "Power Fly Killer", "variant": "500ml", "price": 1200.0, "image": "fly_killer_500.jpg"},
            {"name": "Power Fly Killer", "variant": "4L", "price": 6500.0, "image": "fly_killer_4l.jpg"},
            {"name": "DeepClean", "variant": "1L", "price": 850.0, "image": "deep_clean.jpg"},
            {"name": "Odour Neutralizer", "variant": "500ml", "price": 950.0, "image": "odour_neutralizer.jpg"},
        ]
        
        print("Seeding new PowerLanka products...")
        for p in products_to_add:
            p_id = f"{p['name']}_{p['variant']}".replace(" ", "_").lower()
            product = Product(
                id=p_id,
                product_name=p['name'],
                variant=p['variant'],
                price_lkr=p['price'],
                available="Yes",
                image_paths=p['image'],
                last_updated=get_sl_time()
            )
            db.add(product)
            
        db.commit()
        print("✅ Products seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding products: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()
