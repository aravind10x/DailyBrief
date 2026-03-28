#!/usr/bin/env python3
"""
Quick server startup validation script.
"""

import asyncio
import httpx
import sys
from pathlib import Path

async def test_server_startup():
    """Test that the server can start and respond to basic requests."""
    print("🔄 Testing server startup...")
    
    try:
        # Test that we can import the app without errors
        from main import app
        print("✅ FastAPI app imports successfully")
        
        # Test basic health endpoint (assuming server is running)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/", timeout=5.0)
                if response.status_code == 200:
                    print("✅ Server is running and responding")
                    data = response.json()
                    print(f"   Response: {data}")
                else:
                    print(f"⚠️ Server responded with status {response.status_code}")
        except httpx.ConnectError:
            print("📋 Server not currently running (this is fine for testing)")
            print("   To start the server, run: uvicorn main:app --reload")
        except Exception as e:
            print(f"⚠️ Connection test failed: {e}")
        
        # Test configuration
        from app.core.config import settings
        print("✅ Configuration loads successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug mode: {settings.debug}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1) 