import psycopg
from app.core.env_loader import load_project_env
import os

# Load environment variables from selected env file.
load_project_env()

DATABASE_URL = os.getenv("DATABASE_URL")
# Remove the +psycopg from URL for direct psycopg connection
conn_url = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
print(f"Attempting to connect to: {conn_url[:50]}...")

try:
    # Test the connection
    conn = psycopg.connect(conn_url)
    print("✓ Successfully connected to Neon PostgreSQL!")
    
    # Test a simple query
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✓ PostgreSQL version: {version[0][:50]}...")
    
    cur.close()
    conn.close()
    print("✓ Connection closed successfully")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
