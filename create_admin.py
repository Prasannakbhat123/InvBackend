"""
Script to create initial admin user in Supabase database
Run this before testing the API
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import UserTable
from app.core.security import hash_password
from app.core.env_loader import load_project_env
import os

# Load environment variables from selected env file.
load_project_env()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    """Create initial admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(UserTable).filter(UserTable.user_username == "admin").first()
        
        if existing_admin:
            print(f"✓ Admin user already exists!")
            print(f"  User ID: {existing_admin.user_id}")
            print(f"  Username: {existing_admin.user_username}")
            print(f"  Role: {existing_admin.role}")
            return
        
        # Create admin user
        admin_user = UserTable(
            user_id="ADM001",
            user_username="admin",
            user_password=hash_password("admin123"),
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Admin user created successfully!")
        print(f"  User ID: {admin_user.user_id}")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  Role: {admin_user.role}")
        print(f"\nYou can now use these credentials to login.")
        
    except Exception as e:
        print(f"✗ Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("Creating Initial Admin User".center(60))
    print("="*60)
    print()
    create_admin()
    print()
