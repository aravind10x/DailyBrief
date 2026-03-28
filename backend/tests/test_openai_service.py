import pytest
from app.services.openai_service import OpenAIService
from app.core.config import settings


def azure_openai_is_configured() -> bool:
    return all(
        [
            settings.azure_openai_api_key,
            settings.azure_openai_endpoint,
            settings.azure_openai_deployment_name,
        ]
    )


@pytest.mark.asyncio
async def test_openai_service_initialization():
    """Test OpenAI service initialization."""
    service = OpenAIService()
    assert service is not None
    assert service.client is not None
    assert service.deployment_name is not None
    print(f"✅ OpenAI service initialized with deployment: {service.deployment_name}")

def test_openai_configuration():
    """Test that Azure OpenAI is properly configured."""
    if not azure_openai_is_configured():
        pytest.skip("Azure OpenAI is not configured in this environment")

    assert settings.azure_openai_api_key != "", "Azure OpenAI API key should be set"
    assert settings.azure_openai_endpoint != "", "Azure OpenAI endpoint should be set"
    assert settings.azure_openai_deployment_name != "", "Azure OpenAI deployment name should be set"
    print("✅ Azure OpenAI configuration is properly set")

@pytest.mark.asyncio
async def test_daily_tasks_generation():
    """Test daily tasks generation (mock test - doesn't call actual API)."""
    service = OpenAIService()
    
    # Test that the service has the right methods
    assert hasattr(service, 'generate_daily_tasks')
    assert hasattr(service, 'generate_weekly_okrs')
    
    print("✅ OpenAI service has required methods")

@pytest.mark.asyncio
async def test_prompt_building():
    """Test prompt building methods."""
    service = OpenAIService()
    
    # Test daily tasks prompt building
    memory_context = "Test startup context"
    unfinished_tasks = [{"title": "Test task", "estimated_duration": 60}]
    
    prompt = service._build_daily_tasks_prompt(memory_context, unfinished_tasks)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "Test startup context" in prompt
    assert "Test task" in prompt
    
    print("✅ Daily tasks prompt building works correctly")
    
    # Test weekly OKRs prompt building
    historical_okrs = [{"objective_text": "Historical objective", "key_results": "Historical KR"}]
    
    weekly_prompt = service._build_weekly_okrs_prompt(memory_context, historical_okrs)
    
    assert isinstance(weekly_prompt, str)
    assert len(weekly_prompt) > 0
    assert "Test startup context" in weekly_prompt
    
    print("✅ Weekly OKRs prompt building works correctly")
