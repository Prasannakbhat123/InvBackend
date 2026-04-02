"""
Test script to verify API endpoints and database storage
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

# Global variable to store auth token
auth_token = None

def test_health_check():
    """Test if the server is running"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/docs")
        if response.status_code == 200:
            print_success("Backend server is running")
            print_info(f"Swagger docs available at: {BASE_URL.replace('/api/v1', '')}/docs")
            return True
        else:
            print_error(f"Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend server. Make sure it's running on http://127.0.0.1:8000")
        return False

def create_admin_user():
    """Create initial admin user directly in the database"""
    print_section("2. Creating Admin User")
    
    # We'll try to login first, if it fails we need manual intervention
    print_info("Note: Admin user creation requires manual database setup or existing admin")
    print_warning("For first time setup, you may need to create admin user manually in database:")
    print_info("INSERT INTO user_table (user_id, user_username, user_password, role) VALUES")
    print_info("('ADM001', 'admin', '<hashed_password>', 'admin');")
    return None

def test_login(username="admin", password="admin123"):
    """Test user login"""
    print_section("3. Testing Login")
    global auth_token
    
    try:
        payload = {
            "user_username": username,
            "user_password": password
        }
        
        print_info(f"Attempting to login as: {username}")
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data['access_token']
            print_success(f"Login successful!")
            print_info(f"User ID: {data.get('user_id')}")
            print_info(f"Role: {data.get('role')}")
            print_info(f"Token: {auth_token[:20]}...")
            return auth_token
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def test_create_product(token):
    """Test creating a product"""
    print_section("4. Testing Product Creation")
    
    if not token:
        print_warning("Skipping - no auth token available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "product_name": "Test Rose Plant",
            "product_category": "Roses",
            "product_price": 299.99,
            "product_quantity": 100,
            "product_description": "Beautiful red rose plant for testing"
        }
        
        print_info("Creating product: Test Rose Plant")
        response = requests.post(f"{BASE_URL}/products", json=payload, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            product_id = data.get('product_id')
            print_success(f"Product created successfully!")
            print_info(f"Product ID: {product_id}")
            print_info(f"Product data: {json.dumps(data, indent=2)}")
            return product_id
        else:
            print_error(f"Product creation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating product: {str(e)}")
        return None

def test_get_products(token):
    """Test retrieving all products"""
    print_section("5. Testing Get All Products")
    
    if not token:
        print_warning("Skipping - no auth token available")
        return []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info("Fetching all products...")
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            product_count = len(data) if isinstance(data, list) else 0
            print_success(f"Retrieved {product_count} products from database")
            
            if product_count > 0:
                print_info("First product:")
                print_info(json.dumps(data[0] if isinstance(data, list) else data, indent=2))
            
            return data
        else:
            print_error(f"Failed to get products: {response.status_code}")
            print_error(f"Response: {response.text}")
            return []
    except Exception as e:
        print_error(f"Error getting products: {str(e)}")
        return []

def test_get_product_by_id(token, product_id):
    """Test retrieving a specific product"""
    print_section("6. Testing Get Product by ID")
    
    if not token or not product_id:
        print_warning("Skipping - no auth token or product ID available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info(f"Fetching product: {product_id}")
        response = requests.get(f"{BASE_URL}/products/{product_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Product retrieved successfully!")
            print_info(f"Product data: {json.dumps(data, indent=2)}")
            return data
        else:
            print_error(f"Failed to get product: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error getting product: {str(e)}")
        return None

def test_create_order(token, product_id):
    """Test creating an order"""
    print_section("7. Testing Order Creation")
    
    if not token or not product_id:
        print_warning("Skipping - no auth token or product ID available")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "order_buyer_name": "Test Customer",
            "order_buyer_number": "+919876543210",
            "order_status": "pending",
            "order_total_amount": 599.98,
            "products": [
                {
                    "product_id": product_id,
                    "product_quantity": 2
                }
            ]
        }
        
        print_info("Creating order with 2 units of product")
        response = requests.post(f"{BASE_URL}/orders", json=payload, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            order_id = data.get('order_id')
            print_success(f"Order created successfully!")
            print_info(f"Order ID: {order_id}")
            print_info(f"Order data: {json.dumps(data, indent=2)}")
            return order_id
        else:
            print_error(f"Order creation failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating order: {str(e)}")
        return None

def test_get_orders(token):
    """Test retrieving all orders"""
    print_section("8. Testing Get All Orders")
    
    if not token:
        print_warning("Skipping - no auth token available")
        return []
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info("Fetching all orders...")
        response = requests.get(f"{BASE_URL}/orders", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            order_count = len(data) if isinstance(data, list) else 0
            print_success(f"Retrieved {order_count} orders from database")
            
            if order_count > 0:
                print_info("First order:")
                print_info(json.dumps(data[0] if isinstance(data, list) else data, indent=2))
            
            return data
        else:
            print_error(f"Failed to get orders: {response.status_code}")
            print_error(f"Response: {response.text}")
            return []
    except Exception as e:
        print_error(f"Error getting orders: {str(e)}")
        return []

def test_summary():
    """Print test summary"""
    print_section("Test Summary")
    print_success("API testing completed!")
    print_info("Check the results above to verify:")
    print_info("  1. Backend server is running")
    print_info("  2. Authentication works")
    print_info("  3. Products can be created and retrieved")
    print_info("  4. Orders can be created and retrieved")
    print_info("  5. Data is persisting in Supabase database")

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Windscapes Backend API Test Suite{RESET}".center(70))
    print(f"{BLUE}Testing Supabase Database Integration{RESET}".center(70))
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Test 1: Health check
    if not test_health_check():
        print_error("\nBackend is not running. Please start it first:")
        print_info("cd c:\\ERP\\windscapes-backend")
        print_info("C:/ERP/.venv/Scripts/python.exe run.py")
        return
    
    # Test 2: Create admin (informational)
    create_admin_user()
    
    # Test 3: Login
    token = test_login()
    
    if not token:
        print_warning("\nCannot proceed without authentication.")
        print_info("Please create an admin user in Supabase database:")
        print_info("1. Go to Supabase dashboard")
        print_info("2. Open SQL Editor")
        print_info("3. Run: INSERT INTO user_table (user_id, user_username, user_password, role)")
        print_info("       VALUES ('ADM001', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIw3UdFNHm', 'admin');")
        print_info("4. This creates user: admin / password: admin123")
        return
    
    # Test 4-6: Product operations
    product_id = test_create_product(token)
    test_get_products(token)
    
    if product_id:
        test_get_product_by_id(token, product_id)
    
    # Test 7-8: Order operations
    if product_id:
        order_id = test_create_order(token, product_id)
        test_get_orders(token)
    
    # Summary
    test_summary()
    
    print(f"\n{GREEN}All tests completed! Check Supabase dashboard to verify data storage.{RESET}\n")

if __name__ == "__main__":
    main()
