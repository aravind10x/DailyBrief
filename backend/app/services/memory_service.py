import asyncio
from typing import Dict, List, Any, Optional
from contextlib import AsyncExitStack
import logging
import json

from mcp import ClientSession
from mcp.client.sse import sse_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class MemoryService:
    """
    OpenMemory MCP Client using proper MCP protocol with SSE transport
    """
    
    def __init__(self):
        # Parse the MCP URL
        self.mcp_url = settings.openmemory_mcp_url
        # Expected format: http://localhost:8765/mcp/openmemory/sse/<user-id>
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Extract user ID for context
        parts = self.mcp_url.split('/')
        self.user_id = parts[-1] if len(parts) > 0 else "default"
        
        logger.info(f"Initialized MemoryService for user: {self.user_id}")
    
    async def __aenter__(self):
        await self._connect_to_server()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.aclose()
    
    async def _connect_to_server(self):
        """Connect to the OpenMemory MCP server via SSE"""
        try:
            # Connect using SSE transport
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(self.mcp_url)
            )
            self.read, self.write = sse_transport
            
            # Create session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.read, self.write)
            )
            
            # Initialize the session
            await self.session.initialize()
            
            # List available tools for debugging
            response = await self.session.list_tools()
            tools = response.tools
            logger.info(f"Connected to OpenMemory MCP server with tools: {[tool.name for tool in tools]}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise Exception(f"MCP connection failed: {e}")
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool using the MCP session"""
        if not self.session:
            raise Exception("MCP session not initialized")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise Exception(f"Tool call failed: {e}")
    
    async def add_memory(self, text: str, memory_type: str = "general") -> Dict[str, Any]:
        """
        Add a new memory to OpenMemory using proper MCP tool call
        """
        arguments = {
            "text": f"[{memory_type}] {text}"
        }
        result = await self._call_tool("add_memories", arguments)
        
        # Handle MCP result and server-side validation errors
        if hasattr(result, 'isError') and result.isError:
            # Even if there's a server validation error, the memory might still be added
            # This is a known issue with OpenMemory server output format
            logger.warning(f"OpenMemory server validation error (likely harmless): {result.content}")
            return {
                "success": True, 
                "warning": "Server validation error but memory may have been added",
                "details": str(result.content) if hasattr(result, 'content') else str(result)
            }
        elif hasattr(result, 'content'):
            return {"success": True, "content": result.content}
        return {"success": True, "result": str(result)}
    
    async def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by query using proper MCP tool call
        """
        arguments = {
            "query": query
        }
        result = await self._call_tool("search_memory", arguments)
        
        # Parse MCP result
        memories = []
        if hasattr(result, 'content'):
            content = result.content
            if isinstance(content, list):
                # Handle list of TextContent objects
                for item in content:
                    if hasattr(item, 'text'):
                        try:
                            parsed = json.loads(item.text)
                            if isinstance(parsed, list):
                                memories.extend(parsed)
                            else:
                                memories.append(parsed)
                        except:
                            memories.append({"text": item.text})
                    else:
                        memories.append(item)
                memories = memories[:limit]
            elif isinstance(content, str):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        memories = parsed[:limit]
                except:
                    # If it's just text, treat as single memory
                    memories = [{"text": content}]
        
        return memories
    
    async def list_memories(self) -> List[Dict[str, Any]]:
        """
        List all memories using proper MCP tool call
        """
        result = await self._call_tool("list_memories", {})
        
        # Parse MCP result
        memories = []
        if hasattr(result, 'content'):
            content = result.content
            if isinstance(content, list):
                # Handle list of TextContent objects
                for item in content:
                    if hasattr(item, 'text'):
                        try:
                            parsed = json.loads(item.text)
                            if isinstance(parsed, list):
                                memories.extend(parsed)
                            else:
                                memories.append(parsed)
                        except:
                            memories.append({"text": item.text})
                    else:
                        memories.append(item)
            elif isinstance(content, str):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        memories = parsed
                except:
                    memories = [{"text": content}]
        
        return memories
    
    async def delete_all_memories(self) -> Dict[str, Any]:
        """
        Delete all memories (use with caution) using proper MCP tool call
        """
        result = await self._call_tool("delete_all_memories", {})
        
        if hasattr(result, 'content'):
            return {"success": True, "content": result.content}
        return {"success": True, "result": str(result)}
    
    # Specialized methods for behavioral pattern learning
    async def store_startup_context(self, context: str, user_id: str) -> Dict[str, Any]:
        """
        DEPRECATED: Use StructuredContextService.store_context() instead
        This method is kept for backward compatibility with existing code
        """
        logger.warning("store_startup_context is deprecated. Use StructuredContextService instead.")
        return {"success": True, "memories_stored": 0, "deprecated": True}
    
    async def update_startup_context(self, additional_context: str, user_id: str) -> Dict[str, Any]:
        """
        DEPRECATED: Use StructuredContextService.store_context() instead
        This method is kept for backward compatibility with existing code
        """
        logger.warning("update_startup_context is deprecated. Use StructuredContextService instead.")
        return {"success": True, "deprecated": True}
    
    async def get_startup_context(self, user_id: str) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Use StructuredContextService.get_context() instead
        """
        logger.warning("get_startup_context is deprecated. Use StructuredContextService instead.")
        return []
    
    async def store_task_completion(self, task_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Store task completion as large, comprehensive memories with full context
        """
        task_title = task_data.get('task_title', 'Unknown task')
        
        # Create a comprehensive task completion memory with all details
        completion_details = []
        completion_details.append(f"TASK: {task_title}")
        completion_details.append(f"STATUS: {task_data.get('status', 'done')}")
        completion_details.append(f"COMPLETED: {task_data.get('completion_time', 'unknown date')}")
        
        # Add duration analysis if available
        if 'estimated_duration' in task_data and 'actual_duration' in task_data:
            est_dur = task_data['estimated_duration']
            act_dur = task_data['actual_duration']
            variance = act_dur - est_dur
            variance_text = f"took {variance} minutes longer" if variance > 0 else f"finished {abs(variance)} minutes early" if variance < 0 else "finished exactly on time"
            completion_details.append(f"DURATION: Estimated {est_dur} minutes, actually took {act_dur} minutes ({variance_text})")
        
        # Add insights if available
        if 'insights' in task_data and task_data['insights']:
            completion_details.append(f"INSIGHTS: {task_data['insights']}")
        
        # Combine into comprehensive memory
        complete_memory = "\n".join(completion_details)
        comprehensive_memory = f"COMPREHENSIVE TASK COMPLETION RECORD:\n{complete_memory}\n\nThis complete task record includes all performance data, insights, and lessons learned. Use this information to improve future task estimates, identify patterns in execution, and apply learned insights to similar tasks in daily planning."
        
        await self.add_memory(comprehensive_memory, "task_completion")
        
        return {"success": True, "memories_stored": 1}
    
    async def store_weekly_okr(self, okr_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Store weekly OKR as large, comprehensive memory with complete context
        """
        week_start = okr_data.get('week_start', 'Unknown week')
        
        # Build comprehensive OKR memory
        okr_details = []
        okr_details.append(f"WEEK STARTING: {week_start}")
        
        # Add all objectives with their key results
        objectives = okr_data.get('objectives', [])
        for i, obj in enumerate(objectives, 1):
            objective_text = obj.get('objective', 'Unknown objective')
            key_results = obj.get('key_results', [])
            
            okr_details.append(f"\nOBJECTIVE {i}: {objective_text}")
            for j, kr in enumerate(key_results, 1):
                okr_details.append(f"  KEY RESULT {j}: {kr}")
        
        # Add strategic context if available
        if 'context' in okr_data and okr_data['context']:
            okr_details.append(f"\nSTRATEGIC CONTEXT: {okr_data['context']}")
        
        # Combine into comprehensive memory
        complete_okr = "\n".join(okr_details)
        comprehensive_memory = f"COMPREHENSIVE WEEKLY OKR RECORD:\n{complete_okr}\n\nThis complete weekly OKR record includes all objectives, key results, and strategic context. Daily task planning should align with these objectives and contribute to achieving the specified key results. Use this comprehensive context to ensure all daily tasks advance the weekly goals."
        
        await self.add_memory(comprehensive_memory, "weekly_okr")
        
        return {"success": True, "memories_stored": 1}
    
    async def store_approval_pattern(self, approval_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Store user approval patterns as comprehensive, detailed memory
        """
        # Build comprehensive approval pattern memory
        pattern_details = []
        pattern_details.append("USER APPROVAL PATTERNS AND PREFERENCES:")
        
        # Add specific patterns
        if approval_data.get('prefers_morning_tasks'):
            pattern_details.append("- Prefers morning tasks for strategic work and complex decision-making")
        if approval_data.get('likes_time_boxed_estimates'):
            pattern_details.append("- Likes time-boxed estimates for better planning and execution tracking")
        if approval_data.get('focuses_on_high_impact'):
            pattern_details.append("- Focuses on high-impact activities that drive strategic outcomes")
        
        # Add context if available
        context = approval_data.get('context', '')
        if context:
            pattern_details.append(f"\nCONTEXT: {context}")
        
        # Add any additional patterns
        for key, value in approval_data.items():
            if key not in ['prefers_morning_tasks', 'likes_time_boxed_estimates', 'focuses_on_high_impact', 'context'] and value:
                pattern_details.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        # Combine into comprehensive memory
        complete_patterns = "\n".join(pattern_details)
        comprehensive_memory = f"COMPREHENSIVE APPROVAL PATTERN ANALYSIS:\n{complete_patterns}\n\nThese patterns were learned from previous task approvals and editing behaviors. Daily task generation should incorporate these preferences to improve acceptance rate and align with user's natural working style and decision-making patterns."
        
        return await self.add_memory(comprehensive_memory, "approval_pattern")
    
    async def get_behavioral_patterns(self, user_id: str) -> str:
        """
        Get behavioral patterns and learning insights from OpenMemory
        This focuses only on dynamic behavioral data, not static context
        """
        # Search for behavioral patterns only
        pattern_queries = [
            f"task completion {user_id}",
            f"task insight {user_id}",
            f"approval pattern {user_id}",
            f"workflow learning {user_id}",
            f"decision pattern {user_id}",
            f"productivity pattern {user_id}",
            f"collaboration pattern {user_id}"
        ]
        
        # Collect behavioral memories with deduplication
        unique_memories = {}
        for query in pattern_queries:
            try:
                memories = await self.search_memory(query, limit=10)
                for memory in memories:
                    memory_id = memory.get('id')
                    if memory_id and memory_id not in unique_memories:
                        unique_memories[memory_id] = memory
            except Exception as e:
                logger.warning(f"Behavioral pattern search query '{query}' failed: {e}")
                continue
        
        # Extract memory text
        pattern_texts = []
        for memory in unique_memories.values():
            memory_text = ""
            if 'memory' in memory:
                memory_text = memory['memory']
            elif 'text' in memory:
                memory_text = memory['text']
            
            if memory_text:
                pattern_texts.append(memory_text)
        
        return "\n\n".join(pattern_texts[:10])  # Limit to top 10 behavioral patterns
    
    async def get_context_for_daily_brief(self, user_id: str) -> str:
        """
        DEPRECATED: Use HybridContextService.get_daily_brief_context() instead
        This method is kept for backward compatibility with existing code
        """
        logger.warning("get_context_for_daily_brief is deprecated. Use HybridContextService instead.")
        
        # Return only behavioral patterns for now
        return await self.get_behavioral_patterns(user_id)
    
    async def get_context_for_weekly_planning(self, user_id: str) -> str:
        """
        Get comprehensive context for weekly planning
        """
        context_queries = [
            f"startup context user {user_id}",
            f"weekly okr user {user_id}",
            f"approval pattern user {user_id}"
        ]
        
        all_memories = []
        for query in context_queries:
            memories = await self.search_memory(query, limit=5)
            all_memories.extend(memories)
        
        context_parts = []
        for memory in all_memories:
            # Handle both 'memory' and 'text' fields for different response formats
            if 'memory' in memory:
                context_parts.append(memory['memory'])
            elif 'text' in memory:
                context_parts.append(memory['text'])
        
        return "\n\n".join(context_parts[:15])

# Lazy initialization function
_memory_service_instance = None

def get_memory_service() -> MemoryService:
    """Get or create the memory service instance"""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService()
    return _memory_service_instance

# For backward compatibility
memory_service = get_memory_service()
