from supabase import create_client, Client
from supabase._async.client import AsyncClient as Client, create_client as create_async_client
from app.core.config import settings
import asyncio

# Async Supabase client for database operations
supabase: Client = None

# Service role client for admin operations
supabase_admin: Client = None

async def init_db():
    """Initialize database connection and run any startup tasks"""
    global supabase, supabase_admin
    
    try:
        # Initialize async clients
        supabase = await create_async_client(settings.supabase_url, settings.supabase_key)
        supabase_admin = await create_async_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Test connection
        response = await supabase.table("tasks").select("*").limit(1).execute()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def get_db():
    """Dependency to get database client"""
    global supabase
    if supabase is None:
        supabase = await create_async_client(settings.supabase_url, settings.supabase_key)
    return supabase

async def get_supabase_client():
    """Get initialized supabase client"""
    global supabase
    if supabase is None:
        supabase = await create_async_client(settings.supabase_url, settings.supabase_key)
    return supabase

async def get_supabase_admin_client():
    """Get initialized supabase admin client (bypasses RLS)"""
    global supabase_admin
    if supabase_admin is None:
        supabase_admin = await create_async_client(settings.supabase_url, settings.supabase_service_role_key)
    return supabase_admin