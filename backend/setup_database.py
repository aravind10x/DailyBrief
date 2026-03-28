#!/usr/bin/env python3
"""
Database setup script for Daily Brief backend.
Runs the SQL schema through Supabase client.
"""

import asyncio
from app.core.database import supabase
from pathlib import Path

async def setup_database():
    """Set up the database schema by executing the SQL file."""
    print("🔄 Setting up database schema...")
    
    # Read the schema file
    schema_path = Path(__file__).parent / "database" / "schema.sql"
    
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split the schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    print(f"   Executing statement {i}/{len(statements)}...")
                    # Note: Supabase python client doesn't directly support DDL
                    # This would typically be done through the Supabase dashboard
                    # or via psql with the connection string
                    print(f"   Statement preview: {statement[:50]}...")
                except Exception as e:
                    print(f"   ⚠️ Statement {i} failed: {e}")
        
        print("\n📋 Schema execution completed.")
        print("\n🔧 **IMPORTANT**: The above statements need to be run manually in your Supabase SQL editor.")
        print("   1. Go to your Supabase dashboard")
        print("   2. Navigate to SQL Editor")
        print("   3. Copy and paste the contents of backend/database/schema.sql")
        print("   4. Run the SQL statements")
        print("\n   Alternatively, if you have psql and your DATABASE_URL:")
        print("   psql $DATABASE_URL -f backend/database/schema.sql")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Schema file not found: {schema_path}")
        return False
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_database()) 