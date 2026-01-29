import sys
import uuid
from datetime import datetime

import os

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import get_db, User

def create_admin_user():
    db = next(get_db())
    try:
        email = "admin@store.lk"
        # Check if exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists. Resetting password...")
            existing.password_hash = "admin123"
            existing.role = "admin"
            db.commit()
        else:
            print(f"Creating new admin user: {email}")
            new_user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash="admin123", # Simple password
                full_name="System Admin",
                role="admin"
            )
            db.add(new_user)
            db.commit()
            
        print("✅ Admin user ready.")
        print("Email: admin@store.lk")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
