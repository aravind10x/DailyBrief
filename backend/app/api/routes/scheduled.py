from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import APIResponse
from app.services.scheduler import get_scheduler_service
from app.core.auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/daily-brief", response_model=APIResponse)
async def trigger_daily_brief_generation():
    """
    Trigger daily brief generation for all users
    Called by Supabase Edge Function
    """
    try:
        scheduler_service = get_scheduler_service()
        await scheduler_service.run_daily_brief_generation()
        
        return APIResponse(
            success=True,
            message="Daily brief generation completed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error in scheduled daily brief generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Daily brief generation failed: {str(e)}"
        )

@router.post("/auto-approval", response_model=APIResponse)
async def trigger_auto_approval():
    """
    Trigger auto-approval job
    Called by Supabase Edge Function
    """
    try:
        scheduler_service = get_scheduler_service()
        await scheduler_service.run_auto_approval_job()
        
        return APIResponse(
            success=True,
            message="Auto-approval job completed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error in scheduled auto-approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Auto-approval job failed: {str(e)}"
        )

@router.post("/memory-consolidation", response_model=APIResponse)
async def trigger_memory_consolidation():
    """
    Trigger memory consolidation job
    Called by Supabase Edge Function
    """
    try:
        scheduler_service = get_scheduler_service()
        await scheduler_service.run_memory_consolidation()
        
        return APIResponse(
            success=True,
            message="Memory consolidation completed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error in scheduled memory consolidation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory consolidation failed: {str(e)}"
        )

@router.post("/manual-daily-brief", response_model=APIResponse)
async def manual_daily_brief_generation(
    user_id: str = Depends(get_current_user_id)
):
    """
    Manual daily brief generation for single user
    """
    try:
        scheduler_service = get_scheduler_service()
        await scheduler_service._generate_daily_brief_for_user(user_id)
        
        return APIResponse(
            success=True,
            message="Daily brief generated successfully"
        )
    
    except Exception as e:
        logger.error(f"Error in manual daily brief generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Daily brief generation failed: {str(e)}"
        )