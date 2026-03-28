from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime, date
from app.models.schemas import (
    WeeklyPlanGenerateRequest,
    WeeklyPlanApprovalRequest,
    WeeklyOKRResponse,
    DraftWeeklyOKRResponse,
    WeeklyOKRUpdate,
    APIResponse
)
from app.core.auth import get_current_user_id
from app.core.database import supabase
from app.services.memory_service import get_memory_service
from app.services.openai_service import get_openai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=List[DraftWeeklyOKRResponse])
async def generate_weekly_plan(
    request: WeeklyPlanGenerateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate draft weekly OKRs (NOT committed)
    """
    try:
        # Get memory context for weekly planning
        memory_service = get_memory_service()
        async with memory_service:
            memory_context = await memory_service.get_context_for_weekly_planning(user_id)
        
        # Get historical OKRs
        historical_response = await supabase.table("weekly_okrs").select("*").eq("user_id", user_id).order("week_start_date", desc=True).limit(5).execute()
        historical_okrs = historical_response.data or []
        
        # Generate OKRs using OpenAI
        openai_service = get_openai_service()
        generation_result = await openai_service.generate_weekly_okrs(
            user_id,
            memory_context,
            historical_okrs
        )
        
        # Get current week start date (Monday)
        today = date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        # Clear existing draft OKRs for this week
        await supabase.table("draft_weekly_okrs").delete().eq("user_id", user_id).eq("week_start_date", week_start).execute()
        
        # Create draft OKRs
        draft_okrs = []
        for okr_data in generation_result.get("okrs", []):
            draft_okr = {
                "user_id": user_id,
                "objective_text": okr_data["objective_text"],
                "key_results": okr_data["key_results"],
                "week_start_date": week_start,
                "generation_context": {
                    "reasoning": okr_data.get("reasoning"),
                    "alignment_with_strategy": okr_data.get("alignment_with_strategy"),
                    "strategic_insights": generation_result.get("strategic_insights"),
                    "generated_at": datetime.now().isoformat()
                }
            }
            draft_okrs.append(draft_okr)
        
        # Insert draft OKRs
        if draft_okrs:
            insert_response = await supabase.table("draft_weekly_okrs").insert(draft_okrs).execute()
            inserted_okrs = insert_response.data
        else:
            inserted_okrs = []
        
        # Convert to response format
        response_okrs = []
        for okr in inserted_okrs:
            response_okrs.append(DraftWeeklyOKRResponse(
                id=okr["id"],
                user_id=okr["user_id"],
                objective_text=okr["objective_text"],
                key_results=okr["key_results"],
                week_start_date=okr["week_start_date"],
                approval_status="draft",
                approved_at=None,
                auto_approved=False,
                memory_id=okr.get("memory_id"),
                generation_context=okr.get("generation_context"),
                created_at=okr["created_at"]
            ))
        
        return response_okrs
    
    except Exception as e:
        logger.error(f"Error generating weekly plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly plan: {str(e)}"
        )

@router.get("/draft", response_model=List[DraftWeeklyOKRResponse])
async def get_draft_weekly_plan(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current week's draft OKRs for review
    """
    try:
        # Get current week start date
        today = date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        # Get draft OKRs for this week
        response = await supabase.table("draft_weekly_okrs").select("*").eq("user_id", user_id).eq("week_start_date", week_start).execute()
        
        draft_okrs = []
        for okr in response.data or []:
            draft_okrs.append(DraftWeeklyOKRResponse(
                id=okr["id"],
                user_id=okr["user_id"],
                objective_text=okr["objective_text"],
                key_results=okr["key_results"],
                week_start_date=okr["week_start_date"],
                approval_status="draft",
                approved_at=None,
                auto_approved=False,
                memory_id=okr.get("memory_id"),
                generation_context=okr.get("generation_context"),
                created_at=okr["created_at"]
            ))
        
        return draft_okrs
    
    except Exception as e:
        logger.error(f"Error fetching draft weekly plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch draft weekly plan: {str(e)}"
        )

@router.put("/draft/{okr_id}")
async def edit_draft_okr(
    okr_id: uuid.UUID,
    okr_update: WeeklyOKRUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Edit draft OKR before approval
    """
    try:
        # Build update data
        update_data = {}
        if okr_update.objective_text is not None:
            update_data["objective_text"] = okr_update.objective_text
        if okr_update.key_results is not None:
            update_data["key_results"] = okr_update.key_results
        
        update_data["updated_at"] = datetime.now()
        
        # Update draft OKR
        response = await supabase.table("draft_weekly_okrs").update(update_data).eq("id", okr_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft OKR not found"
            )
        
        return {"success": True, "message": "Draft OKR updated successfully"}
    
    except Exception as e:
        logger.error(f"Error editing draft OKR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit draft OKR: {str(e)}"
        )

@router.post("/approve", response_model=APIResponse)
async def approve_weekly_plan(
    request: WeeklyPlanApprovalRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Approve and commit weekly OKRs
    """
    try:
        # Get draft OKRs to approve
        draft_response = await supabase.table("draft_weekly_okrs").select("*").eq("user_id", user_id).in_("id", request.okr_ids).execute()
        
        if not draft_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No draft OKRs found to approve"
            )
        
        # Apply modifications and move to operational table
        approved_okrs = []
        for okr in draft_response.data:
            approved_okr = {
                "user_id": user_id,
                "objective_text": okr["objective_text"],
                "key_results": okr["key_results"],
                "week_start_date": okr["week_start_date"],
                "approval_status": "approved",
                "approved_at": datetime.now(),
                "auto_approved": False,
                "memory_id": okr.get("memory_id")
            }
            
            # Apply modifications if provided
            if request.modifications and okr["id"] in request.modifications:
                modifications = request.modifications[okr["id"]]
                approved_okr.update(modifications)
            
            approved_okrs.append(approved_okr)
        
        # Insert approved OKRs
        if approved_okrs:
            await supabase.table("weekly_okrs").insert(approved_okrs).execute()
        
        # Store OKRs in memory for future reference
        memory_service = get_memory_service()
        async with memory_service:
            for okr in approved_okrs:
                await memory_service.store_weekly_okr(okr, user_id)
        
        # Clean up draft OKRs
        await supabase.table("draft_weekly_okrs").delete().eq("user_id", user_id).in_("id", request.okr_ids).execute()
        
        return APIResponse(
            success=True,
            message=f"Weekly plan approved successfully. {len(approved_okrs)} OKRs added to your current week."
        )
    
    except Exception as e:
        logger.error(f"Error approving weekly plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve weekly plan: {str(e)}"
        )

@router.get("/", response_model=List[WeeklyOKRResponse])
async def get_current_weekly_plan(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current week's approved OKRs with progress tracking
    """
    try:
        # Get current week start date
        today = date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        
        # Get approved OKRs for this week
        response = await supabase.table("weekly_okrs").select("*").eq("user_id", user_id).eq("week_start_date", week_start).eq("approval_status", "approved").execute()
        
        okrs = []
        for okr in response.data or []:
            okrs.append(WeeklyOKRResponse(
                id=okr["id"],
                user_id=okr["user_id"],
                objective_text=okr["objective_text"],
                key_results=okr["key_results"],
                week_start_date=okr["week_start_date"],
                approval_status=okr["approval_status"],
                approved_at=okr.get("approved_at"),
                auto_approved=okr.get("auto_approved", False),
                memory_id=okr.get("memory_id"),
                created_at=okr["created_at"]
            ))
        
        return okrs
    
    except Exception as e:
        logger.error(f"Error fetching current weekly plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch current weekly plan: {str(e)}"
        )