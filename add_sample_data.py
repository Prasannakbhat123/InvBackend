"""
Script to add sample nurseries and products for testing
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.nursery import Nursery
from app.models.product import Product
from app.utils.product_id_generator import generate_product_id_8digit
from app.core.env_loader import load_project_env
import os

# Load environment variables from selected env file.
load_project_env()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_sample_data():
    """Add sample nurseries and products"""
    db = SessionLocal()
    
    try:
        # Check if we already have nurseries
        existing_nurseries = db.query(Nursery).count()
        if existing_nurseries > 0:
            print(f"✓ Database already has {existing_nurseries} nurseries")
            
            # Show existing products
            existing_products = db.query(Product).count()
            print(f"✓ Database already has {existing_products} products")
            return
        
        # Create nurseries
        nurseries_data = [
            {"id": "NUR001", "name": "Main Nursery"},
            {"id": "NUR002", "name": "Rose Garden"},
            {"id": "NUR003", "name": "Herb Garden"},
        ]
        
        nurseries = []
        for data in nurseries_data:
            nursery = Nursery(
                nursery_id=data["id"],
                nursery_name=data["name"]
            )
            db.add(nursery)
            nurseries.append(nursery)
        
        db.commit()
        print(f"✓ Created {len(nurseries)} nurseries")
        
        # Create products
        products_data = [
            {
                "nursery_id": nurseries[0].nursery_id,
                "item_name": "Japanese Maple",
                "size": "Small (3-4 ft)",
                "inventory_quantity": 45,
                "ordered_quantity": 12,
                "base_price_per_unit": 89.99,
                "rate_percentage": 25,
            },
            {
                "nursery_id": nurseries[0].nursery_id,
                "item_name": "Blue Spruce",
                "size": "Large (8-10 ft)",
                "inventory_quantity": 8,
                "ordered_quantity": 3,
                "base_price_per_unit": 199.99,
                "rate_percentage": 30,
            },
            {
                "nursery_id": nurseries[1].nursery_id,
                "item_name": "Rose Bush",
                "size": "Medium (2-3 ft)",
                "inventory_quantity": 67,
                "ordered_quantity": 23,
                "base_price_per_unit": 34.99,
                "rate_percentage": 20,
            },
            {
                "nursery_id": nurseries[2].nursery_id,
                "item_name": "Lavender",
                "size": "Small (1-2 ft)",
                "inventory_quantity": 156,
                "ordered_quantity": 45,
                "base_price_per_unit": 12.99,
                "rate_percentage": 15,
            },
            {
                "nursery_id": nurseries[0].nursery_id,
                "item_name": "Cherry Blossom",
                "size": "Medium (5-6 ft)",
                "inventory_quantity": 25,
                "ordered_quantity": 8,
                "base_price_per_unit": 149.99,
                "rate_percentage": 28,
            },
        ]
        
        for data in products_data:
            product_id = generate_product_id_8digit(
                data["nursery_id"], 
                data["size"], 
                data["item_name"]
            )
            product = Product(
                product_id=product_id,
                **data
            )
            db.add(product)
        
        db.commit()
        print(f"✓ Created {len(products_data)} products")
        
        print("\n" + "="*60)
        print("✓ Sample data added successfully!")
        print("="*60)
        print("\nNurseries:")
        for n in nurseries:
            print(f"  - {n.nursery_id}: {n.nursery_name}")
        
        print("\nProducts: Check the admin dashboard to see all products")
        
    except Exception as e:
        print(f"✗ Error adding sample data: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("Adding Sample Data".center(60))
    print("="*60)
    print()
    add_sample_data()
    print()
