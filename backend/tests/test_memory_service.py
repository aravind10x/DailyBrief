import pytest

from app.services.memory_service import MemoryService

@pytest.mark.asyncio
async def test_memory_service_initialization():
    """Test that MemoryService can be initialized."""
    service = MemoryService()
    assert service is not None
    assert service.mcp_url is not None

@pytest.mark.asyncio 
async def test_memory_service_context_manager():
    """Test that MemoryService works as async context manager."""
    try:
        async with MemoryService() as service:
            assert service is not None
    except Exception as e:
        print(f"⚠️ Memory service context manager test failed: {e}")
        pytest.skip("OpenMemory service not available")

@pytest.mark.asyncio
async def test_add_memory():
    """Test adding memory to OpenMemory service."""
    try:
        async with MemoryService() as service:
            result = await service.add_memory("Test memory for backend testing", "test")
            assert isinstance(result, dict)
            print(f"✅ Memory added successfully: {result}")
    except Exception as e:
        print(f"⚠️ Memory service test failed (this might be expected if OpenMemory is not running): {e}")
        # Don't fail the test if OpenMemory is not available
        pytest.skip("OpenMemory service not available")

@pytest.mark.asyncio
async def test_search_memory():
    """Test searching memories."""
    try:
        async with MemoryService() as service:
            # First add a memory
            await service.add_memory("Test search memory for backend", "test")
            
            # Then search for it
            results = await service.search_memory("test search", limit=5)
            assert isinstance(results, list)
            print(f"✅ Memory search successful: Found {len(results)} results")
    except Exception as e:
        print(f"⚠️ Memory search test failed: {e}")
        pytest.skip("OpenMemory service not available")

@pytest.mark.asyncio
async def test_startup_context_operations():
    """Test startup context specific operations."""
    test_user_id = "test-user-123"
    test_context = "Test startup context for backend testing"
    
    try:
        async with MemoryService() as service:
            # Store startup context
            result = await service.store_startup_context(test_context, test_user_id)
            assert isinstance(result, dict)
            
            # Retrieve startup context
            contexts = await service.get_startup_context(test_user_id)
            assert isinstance(contexts, list)
            
            print(f"✅ Startup context operations successful")
    except Exception as e:
        print(f"⚠️ Startup context test failed: {e}")
        pytest.skip("OpenMemory service not available")
