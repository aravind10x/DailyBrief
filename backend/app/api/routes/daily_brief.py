from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import uuid
from datetime import datetime, date
from app.models.schemas import (
    DailyBriefGenerateRequest,
    DailyBriefApprovalRequest,
    DailyBriefResponse,
    DraftTaskResponse,
    TaskUpdate,
    APIResponse
)
from app.core.auth import get_current_user_id
from app.core.database import get_supabase_client, get_supabase_admin_client
from app.services.memory_service import get_memory_service
from app.services.hybrid_context_service import get_hybrid_context_service
from app.services.openai_service import get_openai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=DailyBriefResponse)
async def generate_daily_brief(
    request: DailyBriefGenerateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate draft daily tasks using memory context (NOT committed)
    """
    try:
        # Get comprehensive context from hybrid service
        hybrid_service = get_hybrid_context_service()
        comprehensive_context = await hybrid_service.get_daily_brief_context(user_id)
        
        # Get unfinished tasks from previous days
        supabase = await get_supabase_admin_client()
        unfinished_response = await supabase.table("tasks").select("*").eq("user_id", user_id).neq("status", "done").execute()
        unfinished_tasks = unfinished_response.data or []
        
        # Generate tasks using OpenAI
        openai_service = get_openai_service()
        generation_result = await openai_service.generate_daily_tasks(
            user_id, 
            comprehensive_context, 
            unfinished_tasks
        )
        
        # Clear existing draft tasks for today
        today = date.today()
        await supabase.table("draft_tasks").delete().eq("user_id", user_id).eq("due_date", today.isoformat()).execute()
        
        # Create draft tasks
        draft_tasks = []
        for task_data in generation_result.get("tasks", []):
            draft_task = {
                "user_id": user_id,
                "title": task_data["title"],
                "estimated_duration": task_data["estimated_duration"],
                "rank": task_data["rank"],
                "due_date": today.isoformat(),
                "generation_context": {
                    "okr_alignment": task_data.get("okr_alignment"),
                    "reasoning": task_data.get("reasoning"),
                    "generated_at": datetime.now().isoformat()
                }
            }
            draft_tasks.append(draft_task)
        
        # Insert draft tasks
        if draft_tasks:
            insert_response = await supabase.table("draft_tasks").insert(draft_tasks).execute()
            inserted_tasks = insert_response.data
        else:
            inserted_tasks = []
        
        # Convert to response format
        response_tasks = []
        for task in inserted_tasks:
            response_tasks.append(DraftTaskResponse(
                id=task["id"],
                user_id=task["user_id"],
                title=task["title"],
                status=task["status"],
                rank=task["rank"],
                estimated_duration=task["estimated_duration"],
                due_date=task["due_date"],
                okr_id=task.get("okr_id"),
                carried_forward=task.get("carried_forward", False),
                memory_id=task.get("memory_id"),
                generation_context=task.get("generation_context"),
                created_at=task["created_at"],
                updated_at=task["updated_at"]
            ))
        
        return DailyBriefResponse(
            tasks=response_tasks,
            generation_context={
                "carry_forward_decisions": generation_result.get("carry_forward_decisions", []),
                "generation_metadata": {
                    "comprehensive_context_length": len(comprehensive_context),
                    "unfinished_tasks_count": len(unfinished_tasks),
                    "generated_at": datetime.now().isoformat()
                }
            },
            generated_at=datetime.now(),
            ready_for_approval=True
        )
    
    except Exception as e:
        logger.error(f"Error generating daily brief: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily brief: {str(e)}"
        )

@router.get("/draft", response_model=DailyBriefResponse)
async def get_draft_daily_brief(
    user_id: str = Depends(get_current_user_id)
):
    """
    Fetch current draft for review/editing
    """
    try:
        today = date.today()
        
        # Get draft tasks for today
        supabase = await get_supabase_admin_client()
        response = await supabase.table("draft_tasks").select("*").eq("user_id", user_id).eq("due_date", today.isoformat()).order("rank").execute()
        
        draft_tasks = []
        for task in response.data or []:
            draft_tasks.append(DraftTaskResponse(
                id=task["id"],
                user_id=task["user_id"],
                title=task["title"],
                status=task["status"],
                rank=task["rank"],
                estimated_duration=task["estimated_duration"],
                due_date=task["due_date"],
                okr_id=task.get("okr_id"),
                carried_forward=task.get("carried_forward", False),
                memory_id=task.get("memory_id"),
                generation_context=task.get("generation_context"),
                created_at=task["created_at"],
                updated_at=task["updated_at"]
            ))
        
        return DailyBriefResponse(
            tasks=draft_tasks,
            generation_context={},
            generated_at=datetime.now(),
            ready_for_approval=len(draft_tasks) > 0
        )
    
    except Exception as e:
        logger.error(f"Error fetching draft: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch draft: {str(e)}"
        )

@router.put("/draft/{task_id}")
async def edit_draft_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Edit draft task before approval
    """
    try:
        # Build update data
        update_data = {}
        if task_update.title is not None:
            update_data["title"] = task_update.title
        if task_update.estimated_duration is not None:
            update_data["estimated_duration"] = task_update.estimated_duration
        if task_update.rank is not None:
            update_data["rank"] = task_update.rank
        if task_update.status is not None:
            update_data["status"] = task_update.status
        
        update_data["updated_at"] = datetime.now()
        
        # Update draft task
        supabase = await get_supabase_admin_client()
        response = await supabase.table("draft_tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft task not found"
            )
        
        return {"success": True, "message": "Draft task updated successfully"}
    
    except Exception as e:
        logger.error(f"Error editing draft task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit draft task: {str(e)}"
        )

@router.post("/approve", response_model=APIResponse)
async def approve_daily_brief(
    request: DailyBriefApprovalRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Approve and commit daily brief to operational system
    """
    try:
        today = date.today()
        
        # Get draft tasks to approve
        supabase = await get_supabase_client()
        draft_response = await supabase.table("draft_tasks").select("*").eq("user_id", user_id).in_("id", request.task_ids).execute()
        
        if not draft_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No draft tasks found to approve"
            )
        
        # Apply any modifications
        approved_tasks = []
        for task in draft_response.data:
            approved_task = {
                "user_id": user_id,
                "title": task["title"],
                "status": task["status"],
                "rank": task["rank"],
                "estimated_duration": task["estimated_duration"],
                "due_date": task["due_date"],
                "okr_id": task.get("okr_id"),
                "carried_forward": task.get("carried_forward", False),
                "memory_id": task.get("memory_id")
            }
            
            # Apply modifications if provided
            if request.modifications and task["id"] in request.modifications:
                modifications = request.modifications[task["id"]]
                approved_task.update(modifications)
            
            approved_tasks.append(approved_task)
        
        # Move to operational tasks table
        if approved_tasks:
            await supabase.table("tasks").insert(approved_tasks).execute()
        
        # Store approval decision in memory
        memory_service = get_memory_service()
        async with memory_service:
            approval_data = {
                "date": today.isoformat(),
                "approved_tasks": len(approved_tasks),
                "modifications_made": len(request.modifications or {}),
                "approval_timestamp": datetime.now().isoformat()
            }
            await memory_service.store_approval_pattern(approval_data, user_id)
        
        # Clean up draft tasks
        await supabase.table("draft_tasks").delete().eq("user_id", user_id).in_("id", request.task_ids).execute()
        
        return APIResponse(
            success=True,
            message=f"Daily brief approved successfully. {len(approved_tasks)} tasks added to your workflow."
        )
    
    except Exception as e:
        logger.error(f"Error approving daily brief: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve daily brief: {str(e)}"
        )

@router.post("/manual-generate", response_model=DailyBriefResponse)
async def manual_daily_huddle(
    user_id: str = Depends(get_current_user_id)
):
    """
    Manual 'Run Daily Huddle' button for testing
    """
    try:
        # This is the same as generate but with different endpoint for manual triggering
        request = DailyBriefGenerateRequest(force_regenerate=True)
        return await generate_daily_brief(request, user_id)
    
    except Exception as e:
        logger.error(f"Error in manual daily huddle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run daily huddle: {str(e)}"
        )
