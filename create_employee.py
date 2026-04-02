"""
Script to create an employee user for testing
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import UserTable
from app.core.security import hash_password
from app.core.id_generator import generate_user_id
from app.core.env_loader import load_project_env
import os

# Load environment variables from selected env file.
load_project_env()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_employee():
    """Create employee user"""
    db = SessionLocal()
    
    try:
        # Check if employee already exists
        existing_employee = db.query(UserTable).filter(UserTable.user_username == "employee").first()
        
        if existing_employee:
            print(f"✓ Employee user already exists!")
            print(f"  User ID: {existing_employee.user_id}")
            print(f"  Username: {existing_employee.user_username}")
            print(f"  Role: {existing_employee.role}")
            return
        
        # Generate employee ID
        employee_id = generate_user_id(db, "employee")
        
        # Create employee user
        employee_user = UserTable(
            user_id=employee_id,
            user_username="employee",
            user_password=hash_password("emp123"),
            role="employee"
        )
        
        db.add(employee_user)
        db.commit()
        db.refresh(employee_user)
        
        print(f"✓ Employee user created successfully!")
        print(f"  User ID: {employee_user.user_id}")
        print(f"  Username: employee")
        print(f"  Password: emp123")
        print(f"  Role: {employee_user.role}")
        print(f"\nYou can now use these credentials to login.")
        
    except Exception as e:
        print(f"✗ Error creating employee user: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("Creating Employee User".center(60))
    print("="*60)
    print()
    create_employee()
    print()
