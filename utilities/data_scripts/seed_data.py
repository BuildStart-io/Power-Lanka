
import sys
import os

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import SessionLocal, Product, engine, Base
import uuid

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed_products():
    print("Seeding products manually...")
    db = SessionLocal()
    
    # Core Product List from Constraints/Prompts
    products = [
        {
            "name": "Power Fly Killer",
            "variant": "500ml",
            "price": 1590.0,
            "category": "Pest Control",
            "image": "fly_killer_500.jpg" 
        },
        {
            "name": "Power Fly Killer",
            "variant": "4L Refill",
            "price": 9900.0,
            "category": "Pest Control",
            "image": "fly_killer_4l.jpg"
        },
        {
            "name": "Power DeepClean",
            "variant": "500ml",
            "price": 1290.0,
            "category": "Cleaning",
            "image": "deep_clean.jpg"
        },
        {
            "name": "Power Odour Neutralizer",
            "variant": "500ml",
            "price": 1290.0,
            "category": "Cleaning",
            "image": "odour_neutralizer.jpg"
        }
    ]
    
    count = 0
    for p in products:
        p_id = f"{p['name']}_{p['variant']}"
        
        # Check if exists
        exists = db.query(Product).filter(Product.id == p_id).first()
        if not exists:
            new_prod = Product(
                id=p_id,
                product_name=p['name'],
                variant=p['variant'],
                price_lkr=p['price'],
                available="Yes",
                image_paths=p['image'] # Placeholder
            )
            db.add(new_prod)
            count += 1
            print(f"Added: {p_id}")
        else:
            print(f"Skipped (Exists): {p_id}")
    
    db.commit()
    print(f"✅ Successfully seeded {count} products.")
    db.close()

if __name__ == "__main__":
    seed_products()
