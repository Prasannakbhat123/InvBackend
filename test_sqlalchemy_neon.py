from app.core.database import engine, SessionLocal, Base
from sqlalchemy import text
import sys

print("Testing SQLAlchemy connection to Neon DB...")
print("=" * 60)

try:
    # Test 1: Engine connection
    print("\n1. Testing engine connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✓ Engine connected successfully")
        print(f"✓ PostgreSQL version: {version[:60]}...")
    
    # Test 2: Session creation
    print("\n2. Testing session creation...")
    db = SessionLocal()
    result = db.execute(text("SELECT current_database(), current_user"))
    db_name, user = result.fetchone()
    print(f"✓ Session created successfully")
    print(f"✓ Connected to database: {db_name}")
    print(f"✓ Connected as user: {user}")
    db.close()
    
    # Test 3: Check existing tables
    print("\n3. Checking existing tables...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = result.fetchall()
        if tables:
            print(f"✓ Found {len(tables)} existing tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("✓ No tables found (clean database)")
    
    # Test 4: Test table creation capability
    print("\n4. Testing table creation capability...")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                test_value VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("INSERT INTO test_connection (test_value) VALUES ('Neon DB Test')"))
        conn.commit()
        
        result = conn.execute(text("SELECT test_value FROM test_connection LIMIT 1"))
        value = result.fetchone()[0]
        print(f"✓ Table created and data inserted: {value}")
        
        # Cleanup
        conn.execute(text("DROP TABLE test_connection"))
        conn.commit()
        print("✓ Test table cleaned up")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Neon DB is properly configured!")
    print("=" * 60)
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
