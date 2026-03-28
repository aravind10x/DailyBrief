import pytest
import app.core.database as database
from app.core.config import settings


def database_env_is_configured() -> bool:
    return all(
        [
            settings.supabase_url,
            settings.supabase_key,
        ]
    )

@pytest.mark.asyncio
async def test_database_initialization():
    """Test database initialization."""
    if not database_env_is_configured():
        pytest.skip("Supabase is not configured in this environment")

    result = await database.init_db()
    assert result is True, "Database initialization should succeed"
    print("✅ Database initialization successful")

@pytest.mark.asyncio
async def test_supabase_client():
    """Test that Supabase client is properly configured."""
    if not database_env_is_configured():
        pytest.skip("Supabase is not configured in this environment")

    await database.init_db()
    assert database.supabase is not None
    assert hasattr(database.supabase, 'table')
    print("✅ Supabase client configured properly")

@pytest.mark.asyncio
async def test_database_connection():
    """Test basic database connectivity."""
    if not database_env_is_configured():
        pytest.skip("Supabase is not configured in this environment")

    try:
        # Try to access a table (this will test connection)
        await database.init_db()
        response = await database.supabase.table("tasks").select("id").limit(1).execute()
        assert response is not None
        print("✅ Database connection successful")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

@pytest.mark.asyncio
async def test_tables_exist():
    """Test that required tables exist."""
    if not database_env_is_configured():
        pytest.skip("Supabase is not configured in this environment")

    tables_to_check = [
        "tasks",
        "draft_tasks", 
        "weekly_okrs",
        "draft_weekly_okrs",
        "task_logs",
        "llm_usage"
    ]
    
    for table_name in tables_to_check:
        try:
            await database.init_db()
            response = await database.supabase.table(table_name).select("*").limit(1).execute()
            assert response is not None
            print(f"✅ Table '{table_name}' exists and is accessible")
        except Exception as e:
            pytest.fail(f"Table '{table_name}' is not accessible: {e}")
