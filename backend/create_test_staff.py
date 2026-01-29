import sys
import uuid
from datetime import datetime

# Add backend directory to path
sys.path.append('/home/lord/Projects/Power-Lanka-Project/PL_Server/backend')

from app.database import get_db, User

def create_staff_user():
    db = next(get_db())
    try:
        email = "staff@store.lk"
        # Check if exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists. Updating role to 'staff'...")
            existing.role = "staff"
            db.commit()
        else:
            print(f"Creating new staff user: {email}")
            new_user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash="password", # Simple password for testing
                full_name="Staff Member",
                role="staff"
            )
            db.add(new_user)
            db.commit()
            
        print("✅ Staff user ready.")
        print("Email: staff@store.lk")
        print("Password: password")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_staff_user()
