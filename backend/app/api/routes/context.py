from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

from app.core.auth import get_current_user_id
from app.services.structured_context_service import get_structured_context_service
from app.services.context_parser import get_context_parser
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/context",
    tags=["context"]
)

# Request/Response Models
class ContextInitializeRequest(BaseModel):
    raw_content: str
    source: Optional[str] = "frontend_onboarding"

class ContextUpdateRequest(BaseModel):
    context_type: str  # One of: business_overview, current_situation, strategic_context, operational_context
    additional_content: str
    append_mode: bool = True  # If True, append to existing; if False, replace

class ContextResponse(BaseModel):
    context_type: str
    content: str
    preview: str
    character_count: int
    last_updated: datetime

class ContextSummaryResponse(BaseModel):
    available_sections: List[ContextResponse]
    total_character_count: int
    is_initialized: bool
    last_updated: Optional[datetime]

class APIResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None

@router.post("/initialize", response_model=APIResponse)
async def initialize_context(
    request: ContextInitializeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Initialize user's structured context from raw text (onboarding)
    This is called when user first sets up their context via the frontend
    """
    try:
        # Parse the raw content into structured sections
        parser = get_context_parser()
        context_map = parser.parse_startup_context(request.raw_content)
        
        # Store each parsed section
        structured_service = get_structured_context_service()
        results = []
        
        for context_type, content in context_map.items():
            if content:
                result = await structured_service.store_context(
                    user_id=user_id,
                    context_type=context_type,
                    content=content,
                    metadata={
                        "source": request.source,
                        "initialized_at": datetime.now().isoformat(),
                        "raw_content_length": len(request.raw_content)
                    }
                )
                results.append(f"{context_type}: {result['action']} ({result['content_length']} chars)")
            else:
                results.append(f"{context_type}: no content found")
        
        logger.info(f"Context initialized for user {user_id}: {len(context_map)} sections")
        
        return APIResponse(
            success=True,
            message=f"Context initialized successfully with {len([c for c in context_map.values() if c])} sections",
            details={
                "parsed_sections": list(context_map.keys()),
                "results": results,
                "total_content_length": sum(len(c) for c in context_map.values())
            }
        )
        
    except Exception as e:
        logger.error(f"Error initializing context for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize context: {str(e)}"
        )

@router.put("/update", response_model=APIResponse)
async def update_context(
    request: ContextUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update specific context section with additional content
    Used by the Context Settings Drawer for ongoing updates
    """
    try:
        structured_service = get_structured_context_service()
        parser = get_context_parser()
        
        # Validate context type
        valid_types = ["business_overview", "current_situation", "strategic_context", "operational_context"]
        if request.context_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid context_type. Must be one of: {valid_types}"
            )
        
        # Get existing content if appending
        existing_content = ""
        if request.append_mode:
            existing_content = await structured_service.get_context(user_id, request.context_type) or ""
        
        # Format the update
        formatted_update = parser.parse_context_update(request.additional_content, request.context_type)
        
        # Combine content
        if existing_content and request.append_mode:
            updated_content = f"{existing_content}\n\n{formatted_update}"
        else:
            updated_content = formatted_update
        
        # Store updated content
        result = await structured_service.store_context(
            user_id=user_id,
            context_type=request.context_type,
            content=updated_content,
            metadata={
                "source": "frontend_update",
                "updated_at": datetime.now().isoformat(),
                "append_mode": request.append_mode,
                "update_length": len(formatted_update)
            }
        )
        
        logger.info(f"Context updated for user {user_id}: {request.context_type} ({result['action']})")
        
        return APIResponse(
            success=True,
            message=f"Context section '{request.context_type}' updated successfully",
            details={
                "context_type": request.context_type,
                "action": result["action"],
                "content_length": result["content_length"],
                "append_mode": request.append_mode
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update context: {str(e)}"
        )

@router.get("/", response_model=ContextSummaryResponse)
async def get_context_summary(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get summary of all context sections for display in frontend
    Used by Context Settings Drawer and dashboard
    """
    try:
        structured_service = get_structured_context_service()
        parser = get_context_parser()
        
        # Get all context
        all_context = await structured_service.get_all_context(user_id)
        
        # Build response with previews
        available_sections = []
        total_chars = 0
        latest_update = None
        
        for context_type, content in all_context.items():
            if content:
                preview = parser.get_context_preview(content, 150)
                char_count = len(content)
                total_chars += char_count
                
                available_sections.append(ContextResponse(
                    context_type=context_type,
                    content=content,
                    preview=preview,
                    character_count=char_count,
                    last_updated=datetime.now()  # TODO: Get actual timestamp from metadata
                ))
        
        return ContextSummaryResponse(
            available_sections=available_sections,
            total_character_count=total_chars,
            is_initialized=len(available_sections) > 0,
            last_updated=latest_update
        )
        
    except Exception as e:
        logger.error(f"Error getting context summary for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context summary: {str(e)}"
        )

@router.get("/{context_type}", response_model=ContextResponse)
async def get_context_section(
    context_type: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get specific context section
    Used for detailed view or editing
    """
    try:
        # Validate context type
        valid_types = ["business_overview", "current_situation", "strategic_context", "operational_context"]
        if context_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid context_type. Must be one of: {valid_types}"
            )
        
        structured_service = get_structured_context_service()
        parser = get_context_parser()
        
        content = await structured_service.get_context(user_id, context_type)
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No content found for context type: {context_type}"
            )
        
        preview = parser.get_context_preview(content, 200)
        
        return ContextResponse(
            context_type=context_type,
            content=content,
            preview=preview,
            character_count=len(content),
            last_updated=datetime.now()  # TODO: Get actual timestamp from metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context section {context_type} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context section: {str(e)}"
        )

@router.delete("/{context_type}", response_model=APIResponse)
async def delete_context_section(
    context_type: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete specific context section
    Used for cleanup or resetting sections
    """
    try:
        # Validate context type
        valid_types = ["business_overview", "current_situation", "strategic_context", "operational_context"]
        if context_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid context_type. Must be one of: {valid_types}"
            )
        
        structured_service = get_structured_context_service()
        
        result = await structured_service.delete_context(user_id, context_type)
        
        if result["success"]:
            return APIResponse(
                success=True,
                message=f"Context section '{context_type}' deleted successfully",
                details=result
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Unknown error occurred")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting context section {context_type} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete context section: {str(e)}"
        ) 