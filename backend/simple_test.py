#!/usr/bin/env python3
"""
Simple test to verify basic functionality without external dependencies
"""

def test_imports():
    """Test that we can import our modules"""
    try:
        from app.core.config import settings
        print("✅ Config import successful")
        print(f"   Azure OpenAI endpoint configured: {bool(settings.azure_openai_endpoint)}")
        print(f"   Supabase URL configured: {bool(settings.supabase_url)}")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_pydantic_models():
    """Test that our Pydantic models work"""
    try:
        from app.models.schemas import TaskCreate, MemoryContextRequest
        
        # Test task creation
        task = TaskCreate(
            title="Test task",
            estimated_duration=60,
            rank=1
        )
        print("✅ Pydantic models work correctly")
        print(f"   Sample task: {task.title} ({task.estimated_duration}min)")
        return True
    except Exception as e:
        print(f"❌ Pydantic models failed: {e}")
        return False

def test_openai_service_init():
    """Test OpenAI service initialization"""
    try:
        from app.services.openai_service import OpenAIService
        service = OpenAIService()
        print("✅ OpenAI service initialization successful")
        print(f"   Deployment name: {service.deployment_name}")
        return True
    except Exception as e:
        print(f"❌ OpenAI service initialization failed: {e}")
        return False

def test_memory_service_init():
    """Test Memory service initialization"""
    try:
        from app.services.memory_service import MemoryService
        service = MemoryService()
        print("✅ Memory service initialization successful")
        print(f"   Base URL: {service.base_url}")
        return True
    except Exception as e:
        print(f"❌ Memory service initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Simple Backend Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_pydantic_models,
        test_openai_service_init,
        test_memory_service_init,
    ]
    
    results = []
    for test in tests:
        print(f"\n📋 Running: {test.__name__}")
        result = test()
        results.append(result)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️ Some tests failed - check configuration")