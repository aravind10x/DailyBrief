from typing import Dict, List, Optional
from app.core.database import get_supabase_admin_client
import logging

logger = logging.getLogger(__name__)

class StructuredContextService:
    """
    Service for managing structured context storage in Supabase
    This handles the static context part of our hybrid architecture
    """
    
    def __init__(self):
        pass
    
    async def store_context(self, user_id: str, context_type: str, content: str, metadata: Dict = None) -> Dict:
        """
        Store or update structured context for a user
        
        Args:
            user_id: User identifier
            context_type: Type of context ('business_overview', 'current_situation', 'strategic_context', 'operational_context')
            content: Raw context content to store
            metadata: Optional metadata dictionary
        """
        try:
            supabase = await get_supabase_admin_client()
            
            # Check if context of this type already exists
            existing_response = await supabase.table("structured_context").select("id").eq("user_id", user_id).eq("context_type", context_type).execute()
            
            context_data = {
                "user_id": user_id,
                "context_type": context_type,
                "raw_content": content,
                "metadata": metadata or {}
            }
            
            if existing_response.data:
                # Update existing context
                update_response = await supabase.table("structured_context").update(context_data).eq("user_id", user_id).eq("context_type", context_type).execute()
                
                logger.info(f"Updated {context_type} context for user {user_id}")
                return {
                    "success": True,
                    "action": "updated",
                    "context_type": context_type,
                    "content_length": len(content)
                }
            else:
                # Insert new context
                insert_response = await supabase.table("structured_context").insert(context_data).execute()
                
                logger.info(f"Created {context_type} context for user {user_id}")
                return {
                    "success": True,
                    "action": "created", 
                    "context_type": context_type,
                    "content_length": len(content)
                }
                
        except Exception as e:
            logger.error(f"Error storing {context_type} context for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_context(self, user_id: str, context_type: str) -> Optional[str]:
        """
        Retrieve structured context for a user by type
        
        Args:
            user_id: User identifier  
            context_type: Type of context to retrieve
            
        Returns:
            Raw content string or None if not found
        """
        try:
            supabase = await get_supabase_admin_client()
            
            response = await supabase.table("structured_context").select("raw_content").eq("user_id", user_id).eq("context_type", context_type).execute()
            
            if response.data:
                return response.data[0]["raw_content"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving {context_type} context for user {user_id}: {e}")
            return None
    
    async def get_all_context(self, user_id: str) -> Dict[str, str]:
        """
        Retrieve all structured context for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary mapping context_type to raw_content
        """
        try:
            supabase = await get_supabase_admin_client()
            
            response = await supabase.table("structured_context").select("context_type, raw_content").eq("user_id", user_id).execute()
            
            context_map = {}
            for item in response.data:
                context_map[item["context_type"]] = item["raw_content"]
            
            return context_map
            
        except Exception as e:
            logger.error(f"Error retrieving all context for user {user_id}: {e}")
            return {}
    
    async def list_context_types(self, user_id: str) -> List[str]:
        """
        List all context types available for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of context types
        """
        try:
            supabase = await get_supabase_admin_client()
            
            response = await supabase.table("structured_context").select("context_type").eq("user_id", user_id).execute()
            
            return [item["context_type"] for item in response.data]
            
        except Exception as e:
            logger.error(f"Error listing context types for user {user_id}: {e}")
            return []
    
    async def delete_context(self, user_id: str, context_type: str) -> Dict:
        """
        Delete structured context for a user by type
        
        Args:
            user_id: User identifier
            context_type: Type of context to delete
        """
        try:
            supabase = await get_supabase_admin_client()
            
            response = await supabase.table("structured_context").delete().eq("user_id", user_id).eq("context_type", context_type).execute()
            
            logger.info(f"Deleted {context_type} context for user {user_id}")
            return {
                "success": True,
                "action": "deleted",
                "context_type": context_type
            }
            
        except Exception as e:
            logger.error(f"Error deleting {context_type} context for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Lazy initialization function
_structured_context_service_instance = None

def get_structured_context_service() -> StructuredContextService:
    """Get or create the structured context service instance"""
    global _structured_context_service_instance
    if _structured_context_service_instance is None:
        _structured_context_service_instance = StructuredContextService()
    return _structured_context_service_instance 