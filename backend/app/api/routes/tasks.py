from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from datetime import datetime
from app.models.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    APIResponse
)
from app.core.auth import get_current_user_id
from app.core.database import supabase
from app.services.memory_service import get_memory_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str = Depends(get_current_user_id)
):
    """
    Fetch current operational tasks
    """
    try:
        response = await supabase.table("tasks").select("*").eq("user_id", user_id).order("rank").execute()
        
        tasks = []
        for task in response.data or []:
            tasks.append(TaskResponse(
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
                created_at=task["created_at"],
                updated_at=task["updated_at"]
            ))
        
        return tasks
    
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create new task + store creation context in memory
    """
    try:
        # Create task data
        task_data = {
            "user_id": user_id,
            "title": task.title,
            "status": task.status,
            "rank": task.rank,
            "estimated_duration": task.estimated_duration,
            "due_date": task.due_date,
            "okr_id": task.okr_id,
            "carried_forward": task.carried_forward
        }
        
        # Insert task
        response = await supabase.table("tasks").insert(task_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create task"
            )
        
        created_task = response.data[0]
        
        # Store creation context in memory
        memory_service = get_memory_service()
        async with memory_service:
            creation_data = {
                "action": "task_created",
                "task_id": created_task["id"],
                "title": created_task["title"],
                "estimated_duration": created_task["estimated_duration"],
                "created_at": datetime.now().isoformat()
            }
            await memory_service.add_memory(
                f"Task created: {creation_data}", 
                "task_creation"
            )
        
        return TaskResponse(
            id=created_task["id"],
            user_id=created_task["user_id"],
            title=created_task["title"],
            status=created_task["status"],
            rank=created_task["rank"],
            estimated_duration=created_task["estimated_duration"],
            due_date=created_task["due_date"],
            okr_id=created_task.get("okr_id"),
            carried_forward=created_task.get("carried_forward", False),
            memory_id=created_task.get("memory_id"),
            created_at=created_task["created_at"],
            updated_at=created_task["updated_at"]
        )
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update task status + store completion pattern in memory
    """
    try:
        # Get current task for comparison
        current_response = await supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
        
        if not current_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        current_task = current_response.data[0]
        
        # Build update data
        update_data = {}
        if task_update.title is not None:
            update_data["title"] = task_update.title
        if task_update.status is not None:
            update_data["status"] = task_update.status
        if task_update.rank is not None:
            update_data["rank"] = task_update.rank
        if task_update.estimated_duration is not None:
            update_data["estimated_duration"] = task_update.estimated_duration
        if task_update.due_date is not None:
            update_data["due_date"] = task_update.due_date
        if task_update.okr_id is not None:
            update_data["okr_id"] = task_update.okr_id
        
        update_data["updated_at"] = datetime.now()
        
        # Update task
        response = await supabase.table("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        updated_task = response.data[0]
        
        # Log task changes
        if current_task["status"] != updated_task["status"] or current_task["rank"] != updated_task["rank"]:
            await supabase.table("task_logs").insert({
                "user_id": user_id,
                "task_id": task_id,
                "previous_status": current_task["status"],
                "new_status": updated_task["status"],
                "previous_rank": current_task["rank"],
                "new_rank": updated_task["rank"]
            }).execute()
        
        # Store completion pattern in memory if task completed
        if task_update.status == "done" and current_task["status"] != "done":
            memory_service = get_memory_service()
            async with memory_service:
                completion_data = {
                    "action": "task_completed",
                    "task_id": str(task_id),
                    "title": updated_task["title"],
                    "estimated_duration": updated_task["estimated_duration"],
                    "completed_at": datetime.now().isoformat(),
                    "carried_forward": updated_task.get("carried_forward", False)
                }
                await memory_service.store_task_completion(completion_data, user_id)
        
        return TaskResponse(
            id=updated_task["id"],
            user_id=updated_task["user_id"],
            title=updated_task["title"],
            status=updated_task["status"],
            rank=updated_task["rank"],
            estimated_duration=updated_task["estimated_duration"],
            due_date=updated_task["due_date"],
            okr_id=updated_task.get("okr_id"),
            carried_forward=updated_task.get("carried_forward", False),
            memory_id=updated_task.get("memory_id"),
            created_at=updated_task["created_at"],
            updated_at=updated_task["updated_at"]
        )
    
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )

@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete task
    """
    try:
        # Delete task
        response = await supabase.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return APIResponse(
            success=True,
            message="Task deleted successfully"
        )
    
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )