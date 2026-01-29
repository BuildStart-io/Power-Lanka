import uuid
import os
import sys

# Add backend directory to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(project_root, 'backend'))

from app.database import SessionLocal, User

def add_admin(email, password, full_name):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists.")
            return

        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=password, # In production, hash this!
            full_name=full_name
        )
        db.add(new_user)
        db.commit()
        print(f"✅ Admin created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"❌ Error adding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Power Lanka Admin Creation ---")
    email = input("Enter Admin Email: ")
    password = input("Enter Admin Password: ")
    name = input("Enter Full Name: ")
    add_admin(email, password, name)
