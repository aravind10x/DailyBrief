from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    MemoryContextRequest, 
    MemoryContextResponse, 
    MemoryContextListResponse,
    MemoryInsightsResponse
)
from app.core.auth import get_current_user_id
from app.services.memory_service import get_memory_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/context", response_model=MemoryContextResponse)
async def store_initial_context(
    request: MemoryContextRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Store initial startup context in OpenMemory
    """
    try:
        memory_service = get_memory_service()
        async with memory_service:
            result = await memory_service.store_startup_context(
                request.context, 
                user_id
            )
        
        return MemoryContextResponse(
            success=True,
            message="Context stored successfully",
            memory_id=result.get("memory_id")
        )
    
    except Exception as e:
        logger.error(f"Error storing context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store context: {str(e)}"
        )

@router.put("/context", response_model=MemoryContextResponse)
async def update_context(
    request: MemoryContextRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update context by adding additional notes
    """
    try:
        memory_service = get_memory_service()
        async with memory_service:
            result = await memory_service.update_startup_context(
                request.context, 
                user_id
            )
        
        return MemoryContextResponse(
            success=True,
            message="Context updated successfully",
            memory_id=result.get("memory_id")
        )
    
    except Exception as e:
        logger.error(f"Error updating context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update context: {str(e)}"
        )

@router.get("/context", response_model=MemoryContextListResponse)
async def get_context_history(
    user_id: str = Depends(get_current_user_id)
):
    """
    Retrieve chronological context history
    """
    try:
        memory_service = get_memory_service()
        async with memory_service:
            memories = await memory_service.get_startup_context(user_id)
        
        return MemoryContextListResponse(
            contexts=memories,
            total_count=len(memories)
        )
    
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )

@router.get("/insights", response_model=MemoryInsightsResponse)
async def get_memory_insights(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get AI-generated insights from memory patterns
    """
    try:
        # Placeholder analytics until memory-derived aggregation is wired up.
        return MemoryInsightsResponse(
            task_completions=18,
            productive_time="9-11 AM",
            context_strength="Strong",
            weekly_completion_rate=0.75,
            estimated_vs_actual_time={
                "avg_estimation_accuracy": 0.8,
                "tendency": "slightly_overestimate"
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )

@router.delete("/context", response_model=MemoryContextResponse)
async def clear_all_context(
    user_id: str = Depends(get_current_user_id)
):
    """
    Clear all memories (use with caution)
    """
    try:
        memory_service = get_memory_service()
        async with memory_service:
            result = await memory_service.delete_all_memories()
        
        return MemoryContextResponse(
            success=True,
            message="All context cleared successfully"
        )
    
    except Exception as e:
        logger.error(f"Error clearing context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear context: {str(e)}"
        )
