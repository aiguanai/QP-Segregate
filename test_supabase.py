"""
Quick test script for Supabase connection
This is a simple test to verify your Supabase connection string works
"""
import psycopg2

# Replace with your actual connection string from Supabase
CONNECTION_STRING = "postgresql://postgres:9MmID8s718tW7qns@db.sjngjegkghyfzdiiukhf.supabase.co:5432/postgres"

def test_connection():
    """Test Supabase connection"""
    print("Testing Supabase connection...")
    print(f"Host: db.sjngjegkghyfzdiiukhf.supabase.co")
    
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print("✅ Connection successful!")
        print(f"PostgreSQL version: {version[:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your connection string is correct")
        print("2. Verify your Supabase project is active")
        print("3. Check if your network allows connections to Supabase")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
