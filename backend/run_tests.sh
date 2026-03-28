#!/bin/bash

echo "🧪 Running Daily Brief Backend Tests"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    exit 1
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio httpx

# Run tests with verbose output
echo "🚀 Starting test execution..."

# Run tests in order of complexity
echo ""
echo "🔍 Running Health Check Tests..."
pytest tests/test_health.py -v

echo ""
echo "🔍 Running Database Tests..."
pytest tests/test_database.py -v

echo ""
echo "🔍 Running Memory Service Tests..."
pytest tests/test_memory_service.py -v

echo ""
echo "🔍 Running OpenAI Service Tests..."
pytest tests/test_openai_service.py -v

echo ""
echo "🔍 Running API Endpoint Tests..."
pytest tests/test_api_endpoints.py -v

echo ""
echo "🔍 Running Integration Tests..."
pytest tests/test_integration.py -v

echo ""
echo "📊 Running All Tests with Coverage Summary..."
pytest tests/ -v --tb=short

echo ""
echo "✅ Test execution completed!"