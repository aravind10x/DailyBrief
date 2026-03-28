import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.memory_service import memory_service
import json
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Azure OpenAI Assistants API integration for task generation and planning
    """
    
    def __init__(self):
        self._client = None
        self.deployment_name = settings.azure_openai_deployment_name
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client"""
        if self._client is None:
            self._client = openai.AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
        return self._client

    async def generate_daily_tasks(
        self, 
        user_id: str, 
        comprehensive_context: str, 
        # current_okrs: List[Dict[str, Any]], 
        unfinished_tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate daily tasks using OpenAI with comprehensive hybrid context
        """
        
        # Build context-aware prompt
        prompt = self._build_daily_tasks_prompt(
            comprehensive_context, 
            # current_okrs, 
            unfinished_tasks
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI chief-of-staff helping a startup founder plan their daily tasks. You have access to comprehensive context including: business overview, current situation, strategic priorities, weekly OKRs, operational constraints, and behavioral patterns. Use this hierarchical context to generate highly relevant, strategically aligned tasks that leverage the founder's work patterns and drive the business forward."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "generate_daily_tasks",
                        "description": "Generate a prioritized list of daily tasks",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "tasks": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "estimated_duration": {"type": "integer"},
                                            "rank": {"type": "integer"},
                                            "okr_alignment": {"type": "string"},
                                            "reasoning": {"type": "string"}
                                        },
                                        "required": ["title", "estimated_duration", "rank", "okr_alignment", "reasoning"]
                                    }
                                },
                                "carry_forward_decisions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "task_id": {"type": "string"},
                                            "decision": {"type": "string"},
                                            "reasoning": {"type": "string"}
                                        }
                                    }
                                }
                            },
                            "required": ["tasks", "carry_forward_decisions"]
                        }
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "generate_daily_tasks"}}
            )
            
            # Parse tool call response
            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)
            
            # Log usage for cost tracking
            await self._log_usage(
                user_id, 
                "generate_daily_tasks", 
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating daily tasks: {e}")
            raise Exception(f"Task generation failed: {e}")
    
    async def generate_weekly_okrs(
        self, 
        user_id: str, 
        comprehensive_context: str, 
        historical_okrs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate weekly OKRs using OpenAI with comprehensive hybrid context
        """
        
        prompt = self._build_weekly_okrs_prompt(comprehensive_context, historical_okrs)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI chief-of-staff helping a startup founder plan their weekly OKRs. You have access to comprehensive context including business overview, current situation, strategic priorities, operational constraints, and behavioral patterns. Generate 3-5 measurable objectives with specific key results that align with their startup strategy and leverage their work patterns for maximum execution."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "generate_weekly_okrs",
                        "description": "Generate weekly OKRs with objectives and key results",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "okrs": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "objective_text": {"type": "string"},
                                            "key_results": {"type": "string"},
                                            "reasoning": {"type": "string"},
                                            "alignment_with_strategy": {"type": "string"}
                                        },
                                        "required": ["objective_text", "key_results", "reasoning", "alignment_with_strategy"]
                                    }
                                },
                                "strategic_insights": {
                                    "type": "string",
                                    "description": "Key insights from memory context that informed these OKRs"
                                }
                            },
                            "required": ["okrs", "strategic_insights"]
                        }
                    }
                }],
                tool_choice={"type": "function", "function": {"name": "generate_weekly_okrs"}}
            )
            
            # Parse tool call response
            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)
            
            # Log usage
            await self._log_usage(
                user_id, 
                "generate_weekly_okrs", 
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating weekly OKRs: {e}")
            raise Exception(f"Weekly OKR generation failed: {e}")
    
    def _build_daily_tasks_prompt(
        self, 
        comprehensive_context: str, 
        # current_okrs: List[Dict[str, Any]], 
        unfinished_tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Build context-aware prompt for daily task generation using comprehensive hybrid context
        """
        
        # Note: current_okrs might be redundant since they're in comprehensive_context
        # but keeping for backward compatibility and as backup
        # additional_okrs_text = ""
        # if current_okrs:
        #     additional_okrs_text = "\nADDITIONAL OKR DETAILS (if not in context above):\n"
        #     for okr in current_okrs:
        #         additional_okrs_text += f"- {okr.get('objective_text', '')}\n"
        #         additional_okrs_text += f"  Key Results: {okr.get('key_results', '')}\n"
        
        unfinished_text = ""
        if unfinished_tasks:
            unfinished_text = "\nUNFINISHED TASKS FROM PREVIOUS DAY:\n"
            for task in unfinished_tasks:
                unfinished_text += f"- {task.get('title', '')} (Est: {task.get('estimated_duration', 0)}min, Status: {task.get('status', 'unknown')})\n"
        
        prompt = f"""
Based on the comprehensive context below, generate a prioritized list of 3-5 actionable daily tasks that will drive maximum business impact:

{comprehensive_context}


{unfinished_text}

TASK GENERATION GUIDELINES:
1. **Strategic Alignment**: Use the BUSINESS OVERVIEW and STRATEGIC CONTEXT to ensure tasks directly advance core business objectives
2. **Current Priorities**: Reference CURRENT SITUATION and CURRENT WEEK'S OKRS to focus on immediate priorities  
3. **Work Style Optimization**: Apply OPERATIONAL CONTEXT and BEHAVIORAL PATTERNS to optimize task timing, duration, and complexity for optimizing productivity and impact.
4. **Historical Learning**: Leverage BEHAVIORAL PATTERNS and your intuition to set realistic but sufficiently ambitious time estimates and task structures
5. **Carry-Forward Intelligence**: For unfinished tasks, decide based on strategic alignment and current priorities:
   - Carry forward: If still strategically important and aligned with current OKRs
   - Parking lot: If no longer aligned or lower priority
   - Break down: If task is too large based on historical completion patterns

TASK REQUIREMENTS:
- Prioritize by business impact and OKR alignment
- Use realistic time estimates based on historical patterns
- Balance deep work (strategic) with operational necessities
- Ensure each task has clear deliverables and success criteria

Return tasks in priority order with clear reasoning for recommended prioritization.
"""
        return prompt
    
    def _build_weekly_okrs_prompt(
        self, 
        comprehensive_context: str, 
        historical_okrs: List[Dict[str, Any]]
    ) -> str:
        """
        Build context-aware prompt for weekly OKR generation using comprehensive hybrid context
        """
        
        historical_text = ""
        if historical_okrs:
            historical_text = "\nPREVIOUS WEEKLY OKRs (for learning):\n"
            for okr in historical_okrs[-3:]:  # Last 3 weeks
                historical_text += f"- {okr.get('objective_text', '')}\n"
                historical_text += f"  Key Results: {okr.get('key_results', '')}\n"
                historical_text += f"  Week: {okr.get('week_start_date', '')}\n\n"
        
        prompt = f"""
Based on the comprehensive context below, generate 3-5 measurable weekly OKRs that will drive significant business progress:

{comprehensive_context}

{historical_text}

OKR GENERATION GUIDELINES:
1. **Strategic Foundation**: Use BUSINESS OVERVIEW and STRATEGIC CONTEXT to ensure OKRs advance core business objectives
2. **Current Priorities**: Leverage CURRENT SITUATION to focus on the most critical initiatives for this week
3. **Execution Optimization**: Apply OPERATIONAL CONTEXT and BEHAVIORAL PATTERNS to set achievable OKRs that match work capacity and style
4. **Historical Learning**: Reference previous OKR patterns to set realistic yet ambitious targets
5. **Balance & Impact**: Balance strategic breakthroughs with operational excellence

OKR REQUIREMENTS:
- Each objective should be clear, actionable, and achievable within one week
- Key Results must be specific, measurable, and have clear success criteria
- Consider the founder's productivity patterns and working style
- Build on previous OKR outcomes while pushing for meaningful progress
- Ensure OKRs align with both immediate needs and longer-term strategic goals

OUTPUT FORMAT:
Each OKR should include:
- **Objective**: Clear, inspiring weekly goal
- **Key Results**: 2-3 specific, measurable outcomes (use bullet points with metrics)
- **Strategic Reasoning**: Why this OKR matters for the business this week
- **Execution Notes**: How this aligns with the founder's work patterns

Prioritize OKRs by business impact and strategic importance.
"""
        return prompt
    
    async def _log_usage(
        self, 
        user_id: str, 
        endpoint: str, 
        prompt_tokens: int, 
        completion_tokens: int, 
        total_tokens: int
    ):
        """
        Log LLM usage for cost tracking
        """
        try:
            from app.core.database import supabase
            
            # Rough cost estimation for Azure OpenAI
            cost_per_1k_tokens = 0.03  # Approximate, adjust based on your Azure pricing
            cost_estimate = (total_tokens / 1000) * cost_per_1k_tokens
            
            await supabase.table("llm_usage").insert({
                "user_id": user_id,
                "endpoint": endpoint,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "model": self.deployment_name,
                "cost_estimate": cost_estimate,
                "memory_context_used": True
            }).execute()
            
        except Exception as e:
            logger.error(f"Error logging usage: {e}")

# Lazy initialization function
_openai_service_instance = None

def get_openai_service() -> OpenAIService:
    """Get or create the OpenAI service instance"""
    global _openai_service_instance
    if _openai_service_instance is None:
        _openai_service_instance = OpenAIService()
    return _openai_service_instance

# For backward compatibility
openai_service = get_openai_service()