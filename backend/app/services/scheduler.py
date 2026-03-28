import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from app.core.database import supabase

logger = logging.getLogger(__name__)

class ScheduledJobsService:
    """
    Service for handling scheduled jobs like daily brief generation
    """
    
    async def run_daily_brief_generation(self):
        """
        Generate daily briefs for all active users
        Scheduled to run daily at 05:30am
        """
        try:
            logger.info("Starting daily brief generation job")
            
            # Get active users
            users_response = await supabase.rpc('get_users_for_daily_brief').execute()
            active_users = users_response.data or []
            
            generated_count = 0
            for user_data in active_users:
                user_id = user_data['user_id']
                
                try:
                    # Generate daily brief for this user
                    await self._generate_daily_brief_for_user(user_id)
                    generated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error generating daily brief for user {user_id}: {e}")
                    continue
            
            logger.info(f"Daily brief generation completed. Generated for {generated_count} users.")
            
        except Exception as e:
            logger.error(f"Error in daily brief generation job: {e}")
    
    async def _generate_daily_brief_for_user(self, user_id: str):
        """
        Generate daily brief for a specific user
        """
        try:
            # Check if user already has a draft for today
            today = date.today()
            existing_draft = await supabase.table("draft_tasks").select("id").eq("user_id", user_id).eq("due_date", today).limit(1).execute()
            
            if existing_draft.data:
                logger.info(f"User {user_id} already has a draft for today, skipping")
                return
            
            # Get memory context
            from app.services.memory_service import get_memory_service
            memory_service = get_memory_service()
            async with memory_service:
                memory_context = await memory_service.get_context_for_daily_brief(user_id)
            
            # Get current week's approved OKRs
            okrs_response = await supabase.table("weekly_okrs").select("*").eq("user_id", user_id).eq("approval_status", "approved").execute()
            current_okrs = okrs_response.data or []
            
            # Get unfinished tasks from previous days
            unfinished_response = await supabase.table("tasks").select("*").eq("user_id", user_id).neq("status", "done").execute()
            unfinished_tasks = unfinished_response.data or []
            
            # Generate tasks using OpenAI
            from app.services.openai_service import get_openai_service
            openai_service = get_openai_service()
            generation_result = await openai_service.generate_daily_tasks(
                user_id, 
                memory_context, 
                current_okrs, 
                unfinished_tasks
            )
            
            # Create draft tasks
            draft_tasks = []
            for task_data in generation_result.get("tasks", []):
                draft_task = {
                    "user_id": user_id,
                    "title": task_data["title"],
                    "estimated_duration": task_data["estimated_duration"],
                    "rank": task_data["rank"],
                    "due_date": today,
                    "generation_context": {
                        "okr_alignment": task_data.get("okr_alignment"),
                        "reasoning": task_data.get("reasoning"),
                        "generated_at": datetime.now().isoformat(),
                        "generation_type": "scheduled"
                    }
                }
                draft_tasks.append(draft_task)
            
            # Insert draft tasks
            if draft_tasks:
                await supabase.table("draft_tasks").insert(draft_tasks).execute()
                logger.info(f"Generated {len(draft_tasks)} draft tasks for user {user_id}")
            
            # Handle carry-forward decisions
            carry_forward_decisions = generation_result.get("carry_forward_decisions", [])
            for decision in carry_forward_decisions:
                # This would implement the carry-forward logic
                # For now, we'll just log the decisions
                logger.info(f"Carry-forward decision for user {user_id}: {decision}")
            
        except Exception as e:
            logger.error(f"Error generating daily brief for user {user_id}: {e}")
            raise
    
    async def run_auto_approval_job(self):
        """
        Handle auto-approvals and carry-forwards
        Scheduled to run every hour
        """
        try:
            logger.info("Starting auto-approval job")
            
            # Auto-approve weekly OKRs older than 24 hours
            await self._auto_approve_weekly_okrs()
            
            # Handle daily carry-forwards for users who didn't approve
            await self._handle_daily_carry_forwards()
            
            logger.info("Auto-approval job completed")
            
        except Exception as e:
            logger.error(f"Error in auto-approval job: {e}")
    
    async def _auto_approve_weekly_okrs(self):
        """
        Auto-approve weekly OKRs older than 24 hours
        """
        try:
            # Get draft OKRs older than 24 hours
            draft_okrs_response = await supabase.rpc('get_draft_okrs_for_auto_approval').execute()
            draft_okrs = draft_okrs_response.data or []
            
            approved_count = 0
            for okr_data in draft_okrs:
                try:
                    # Move to approved table
                    approved_okr = {
                        "user_id": okr_data["user_id"],
                        "objective_text": okr_data["objective_text"],
                        "key_results": okr_data["key_results"],
                        "week_start_date": okr_data["week_start_date"],
                        "approval_status": "auto_approved",
                        "approved_at": datetime.now(),
                        "auto_approved": True
                    }
                    
                    await supabase.table("weekly_okrs").insert(approved_okr).execute()
                    
                    # Store in memory
                    from app.services.memory_service import get_memory_service
                    memory_service = get_memory_service()
                    async with memory_service:
                        await memory_service.store_weekly_okr(approved_okr, okr_data["user_id"])
                    
                    # Remove from draft
                    await supabase.table("draft_weekly_okrs").delete().eq("id", okr_data["okr_id"]).execute()
                    
                    approved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error auto-approving OKR {okr_data['okr_id']}: {e}")
                    continue
            
            if approved_count > 0:
                logger.info(f"Auto-approved {approved_count} weekly OKRs")
                
        except Exception as e:
            logger.error(f"Error in auto-approval of weekly OKRs: {e}")
    
    async def _handle_daily_carry_forwards(self):
        """
        Handle carry-forwards for users who didn't approve yesterday's brief by 6 AM
        """
        try:
            # This would implement carry-forward logic
            # For now, we'll just log that it's being handled
            logger.info("Handling daily carry-forwards")
            
            # Get users with draft tasks from yesterday who haven't approved
            yesterday = date.today() - timedelta(days=1)
            
            draft_response = await supabase.table("draft_tasks").select("user_id").eq("due_date", yesterday).execute()
            users_with_old_drafts = {row["user_id"] for row in draft_response.data or []}
            
            for user_id in users_with_old_drafts:
                try:
                    # Auto-carry forward logic would go here
                    # For now, we'll just clean up old drafts
                    await supabase.table("draft_tasks").delete().eq("user_id", user_id).eq("due_date", yesterday).execute()
                    logger.info(f"Cleaned up old drafts for user {user_id}")
                    
                except Exception as e:
                    logger.error(f"Error handling carry-forward for user {user_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in daily carry-forward handling: {e}")
    
    async def run_memory_consolidation(self):
        """
        Weekly memory consolidation job
        Scheduled to run Sunday nights
        """
        try:
            logger.info("Starting memory consolidation job")
            
            # This would trigger OpenMemory to consolidate memories
            # For now, we'll just log the action
            logger.info("Memory consolidation would run here")
            
            # Clean up old draft data
            cutoff_date = date.today() - timedelta(days=7)
            
            # Clean old draft tasks
            await supabase.table("draft_tasks").delete().lt("created_at", cutoff_date).execute()
            
            # Clean old draft OKRs
            await supabase.table("draft_weekly_okrs").delete().lt("created_at", cutoff_date).execute()
            
            logger.info("Memory consolidation job completed")
            
        except Exception as e:
            logger.error(f"Error in memory consolidation job: {e}")

# Lazy initialization function
_scheduler_service_instance = None

def get_scheduler_service() -> ScheduledJobsService:
    """Get or create the scheduler service instance"""
    global _scheduler_service_instance
    if _scheduler_service_instance is None:
        _scheduler_service_instance = ScheduledJobsService()
    return _scheduler_service_instance

# For backward compatibility
scheduler_service = get_scheduler_service()