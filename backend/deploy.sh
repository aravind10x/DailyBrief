#!/bin/bash

# Daily Brief Backend Deployment Script

echo "🚀 Starting Daily Brief Backend Deployment"

# Check if required environment variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ] || [ -z "$AZURE_OPENAI_API_KEY" ] || [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "❌ Missing required environment variables"
    echo "Please set: SUPABASE_URL, SUPABASE_KEY, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations (if using Alembic in the future)
echo "🗄️ Setting up database schema..."
echo "Please run the SQL schema in database/schema.sql in your Supabase dashboard"

# Deploy Supabase Edge Functions
echo "🔧 Deploying Supabase Edge Functions..."
if command -v supabase &> /dev/null; then
    supabase functions deploy daily-brief-generator
    supabase functions deploy auto-approval
else
    echo "⚠️ Supabase CLI not found. Please deploy Edge Functions manually."
fi

# Set up cron jobs for Edge Functions
echo "⏰ Setting up scheduled jobs..."
echo "Please configure the following cron schedules in Supabase:"
echo "  - daily-brief-generator: 0 5 * * * (daily at 5:30 AM)"
echo "  - auto-approval: 0 * * * * (hourly)"

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "✅ Daily Brief Backend deployment completed!"
echo "🔗 API will be available at: http://localhost:8000"
echo "📚 API docs available at: http://localhost:8000/docs"