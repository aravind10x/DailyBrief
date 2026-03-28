from typing import Dict, List, Optional
from app.services.structured_context_service import get_structured_context_service
from app.services.memory_service import get_memory_service
from app.core.database import get_supabase_admin_client
import logging

logger = logging.getLogger(__name__)

class HybridContextService:
    """
    Hybrid context service that combines:
    1. Structured context from Supabase (static business context)
    2. Weekly OKRs from Supabase (current objectives)
    3. Behavioral patterns from OpenMemory (dynamic learning)
    """
    
    def __init__(self):
        self.structured_service = get_structured_context_service()
        self.memory_service = get_memory_service()
    
    async def get_daily_brief_context(self, user_id: str) -> str:
        """
        Get comprehensive context for daily brief generation
        Combines all context sources into hierarchical structure
        
        Args:
            user_id: User identifier
            
        Returns:
            Complete context string with clear sections
        """
        try:
            # 1. Get structured context from Supabase (100% preservation)
            structured_context = await self.structured_service.get_all_context(user_id)
            
            # 2. Get current week's OKRs from weekly_okrs table
            weekly_okrs = await self._get_current_weekly_okrs(user_id)
            
            # 3. Get behavioral patterns from OpenMemory
            async with self.memory_service:
                behavioral_patterns = await self.memory_service.get_behavioral_patterns(user_id)
            
            # 4. Assemble hierarchical context
            return self._assemble_hierarchical_context(
                structured_context, weekly_okrs, behavioral_patterns
            )
            
        except Exception as e:
            logger.error(f"Error assembling daily brief context for user {user_id}: {e}")
            return ""
    
    async def _get_current_weekly_okrs(self, user_id: str) -> List[Dict]:
        """
        Get current week's approved OKRs from database
        """
        try:
            supabase = await get_supabase_admin_client()
            
            # Get current week's approved OKRs
            from datetime import date, timedelta
            today = date.today()
            week_start = today - timedelta(days=today.weekday())  # Monday of current week
            
            response = await supabase.table("weekly_okrs").select("*").eq("user_id", user_id).eq("approval_status", "approved").gte("week_start_date", week_start).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error retrieving weekly OKRs for user {user_id}: {e}")
            return []
    
    def _assemble_hierarchical_context(self, structured_context: Dict[str, str], weekly_okrs: List[Dict], behavioral_patterns: str) -> str:
        """
        Assemble all context sources into hierarchical structure
        
        Args:
            structured_context: Dictionary mapping context_type to content
            weekly_okrs: List of current week's OKR records
            behavioral_patterns: Behavioral patterns from OpenMemory
            
        Returns:
            Complete hierarchical context string
        """
        context_sections = []
        
        # Section 1: Business Overview
        business_overview = structured_context.get("business_overview", "")
        if business_overview:
            context_sections.append("=== BUSINESS OVERVIEW ===")
            context_sections.append(business_overview)
            context_sections.append("")  # Empty line for separation
        
        # Section 2: Current Situation
        current_situation = structured_context.get("current_situation", "")
        if current_situation:
            context_sections.append("=== CURRENT SITUATION ===")
            context_sections.append(current_situation)
            context_sections.append("")
        
        # Section 3: Strategic Context
        strategic_context = structured_context.get("strategic_context", "")
        if strategic_context:
            context_sections.append("=== STRATEGIC CONTEXT ===")
            context_sections.append(strategic_context)
            context_sections.append("")
        
        # Section 4: Current Week's OKRs
        if weekly_okrs:
            context_sections.append("=== CURRENT WEEK'S OKRS ===")
            for i, okr in enumerate(weekly_okrs, 1):
                okr_text = f"OBJECTIVE {i}: {okr['objective_text']}\nKEY RESULTS: {okr['key_results']}"
                if okr.get('week_start_date'):
                    okr_text += f"\nWEEK STARTING: {okr['week_start_date']}"
                context_sections.append(okr_text)
            context_sections.append("")
        
        # Section 5: Operational Context
        operational_context = structured_context.get("operational_context", "")
        if operational_context:
            context_sections.append("=== OPERATIONAL CONTEXT ===")
            context_sections.append(operational_context)
            context_sections.append("")
        
        # Section 6: Behavioral Patterns
        if behavioral_patterns:
            context_sections.append("=== BEHAVIORAL PATTERNS ===")
            context_sections.append(behavioral_patterns)
            context_sections.append("")
        
        # Join all sections
        complete_context = "\n\n".join(context_sections).strip()
        
        # Add context summary
        summary_lines = []
        summary_lines.append(f"Context includes: {len([s for s in structured_context.values() if s])} structured sections, {len(weekly_okrs)} current OKRs, {'behavioral patterns' if behavioral_patterns else 'no behavioral patterns'}")
        summary_lines.append(f"Total context length: {len(complete_context)} characters")
        
        context_summary = "CONTEXT SUMMARY: " + ", ".join(summary_lines)
        
        return f"{context_summary}\n\n{complete_context}"
    
    async def get_context_summary(self, user_id: str) -> Dict:
        """
        Get a summary of available context for debugging/monitoring
        """
        try:
            # Get context from all sources
            structured_context = await self.structured_service.get_all_context(user_id)
            weekly_okrs = await self._get_current_weekly_okrs(user_id)
            
            async with self.memory_service:
                behavioral_patterns = await self.memory_service.get_behavioral_patterns(user_id)
            
            return {
                "structured_context": {
                    "available_types": list(structured_context.keys()),
                    "total_length": sum(len(content) for content in structured_context.values())
                },
                "weekly_okrs": {
                    "count": len(weekly_okrs),
                    "objectives": [okr["objective_text"] for okr in weekly_okrs]
                },
                "behavioral_patterns": {
                    "available": bool(behavioral_patterns),
                    "length": len(behavioral_patterns) if behavioral_patterns else 0
                },
                "total_context_length": len(await self.get_daily_brief_context(user_id))
            }
            
        except Exception as e:
            logger.error(f"Error getting context summary for user {user_id}: {e}")
            return {}

# Lazy initialization function
_hybrid_context_service_instance = None

def get_hybrid_context_service() -> HybridContextService:
    """Get or create the hybrid context service instance"""
    global _hybrid_context_service_instance
    if _hybrid_context_service_instance is None:
        _hybrid_context_service_instance = HybridContextService()
    return _hybrid_context_service_instance 