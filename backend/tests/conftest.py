import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    # Import here to avoid circular imports and initialization issues
    from main import app
    
    # Create a simplified app for testing
    test_app = app
    
    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture
async def async_client():
    """Create an async test client for FastAPI app."""
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_user_id():
    """Mock user ID for testing."""
    return str(uuid.uuid4())  # Use proper UUID format

@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers - you'll need a real JWT token for full integration tests."""
    # For now, we'll test without auth and add auth tests separately
    return {}

@pytest.fixture
def sample_context():
    """Sample startup context for testing."""
    return """
    Startup: AI-powered productivity platform for founders
    Goals: 
    - Build MVP by Q2 2024
    - Acquire first 100 users
    - Establish product-market fit
    Current focus: Backend development and user testing
    Constraints: Solo founder, limited budget, need to move fast
    """

@pytest.fixture
def sample_tasks():
    """Sample tasks for testing."""
    return [
        {
            "title": "Complete user authentication",
            "estimated_duration": 120,
            "rank": 1,
            "status": "todo"
        },
        {
            "title": "Write API documentation", 
            "estimated_duration": 90,
            "rank": 2,
            "status": "todo"
        }
    ]