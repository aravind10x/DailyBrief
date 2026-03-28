from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.routes import memory, daily_brief, tasks, weekly_plan, scheduled, context
from app.core.config import settings
from app.core.database import init_db
from app.core.auth import get_current_user

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Daily Brief API",
    description="AI-powered startup co-pilot backend",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(daily_brief.router, prefix="/api/daily-brief", tags=["daily-brief"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(weekly_plan.router, prefix="/api/weekly-plan", tags=["weekly-plan"])
app.include_router(scheduled.router, prefix="/api/scheduled", tags=["scheduled"])

@app.get("/")
async def root():
    return {"message": "Daily Brief API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)