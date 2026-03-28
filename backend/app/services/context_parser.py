from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ContextParser:
    """
    Service for parsing raw context text into structured context types
    Used by both API endpoints and testing scripts
    """
    
    @staticmethod
    def parse_startup_context(content: str) -> Dict[str, str]:
        """
        Parse raw context text into the four context types
        
        Args:
            content: Raw context text (markdown or plain text)
            
        Returns:
            Dictionary with context_type -> content mapping
        """
        context_map = {
            "business_overview": "",
            "current_situation": "",
            "strategic_context": "",
            "operational_context": ""
        }
        
        # Split by actual markdown headers (# at start of line), not just any #
        import re
        
        # Find all markdown headers and their positions
        header_pattern = r'^#+\s+(.+)$'
        lines = content.split('\n')
        
        current_section = None
        current_content_lines = []
        
        for line in lines:
            header_match = re.match(header_pattern, line)
            
            if header_match:
                # Save previous section if we have one
                if current_section is not None and current_content_lines:
                    content_text = '\n'.join(current_content_lines).strip()
                    
                    # Map sections to context types using improved logic
                    title_lower = current_section.lower()
                    
                    if 'company overview' in title_lower or 'business overview' in title_lower or ('overview' in title_lower and len(current_section.split()) <= 3):
                        context_map["business_overview"] += f"\n\n{content_text}" if context_map["business_overview"] else content_text
                        
                    elif 'current' in title_lower or 'stage' in title_lower or 'state' in title_lower or 'situation' in title_lower:
                        context_map["current_situation"] += f"\n\n{content_text}" if context_map["current_situation"] else content_text
                        
                    elif 'strategic' in title_lower or 'strategy' in title_lower or 'priorities' in title_lower or 'key questions' in title_lower or 'questions' in title_lower:
                        context_map["strategic_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["strategic_context"] else f"# {current_section}\n{content_text}"
                        
                    elif 'operational' in title_lower or 'constraints' in title_lower or 'work style' in title_lower or 'historical context' in title_lower or 'decision-making' in title_lower:
                        context_map["operational_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["operational_context"] else f"# {current_section}\n{content_text}"
                    
                    else:
                        # If unclear, add to strategic context for larger sections
                        if len(content_text) > 100:
                            context_map["strategic_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["strategic_context"] else f"# {current_section}\n{content_text}"
                
                # Start new section
                current_section = header_match.group(1).strip()
                current_content_lines = []
            else:
                # Add line to current section
                if current_section is not None:
                    current_content_lines.append(line)
                else:
                    # Content before any header - add to business overview
                    if line.strip():
                        if not context_map["business_overview"]:
                            context_map["business_overview"] = line
                        else:
                            context_map["business_overview"] += f"\n{line}"
        
        # Handle the last section
        if current_section is not None and current_content_lines:
            content_text = '\n'.join(current_content_lines).strip()
            title_lower = current_section.lower()
            
            if 'company overview' in title_lower or 'business overview' in title_lower or ('overview' in title_lower and len(current_section.split()) <= 3):
                context_map["business_overview"] += f"\n\n{content_text}" if context_map["business_overview"] else content_text
                
            elif 'current' in title_lower or 'stage' in title_lower or 'state' in title_lower or 'situation' in title_lower:
                context_map["current_situation"] += f"\n\n{content_text}" if context_map["current_situation"] else content_text
                
            elif 'strategic' in title_lower or 'strategy' in title_lower or 'priorities' in title_lower or 'key questions' in title_lower or 'questions' in title_lower:
                context_map["strategic_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["strategic_context"] else f"# {current_section}\n{content_text}"
                
            elif 'operational' in title_lower or 'constraints' in title_lower or 'work style' in title_lower or 'historical context' in title_lower or 'decision-making' in title_lower:
                context_map["operational_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["operational_context"] else f"# {current_section}\n{content_text}"
            
            else:
                # If unclear, add to strategic context for larger sections
                if len(content_text) > 100:
                    context_map["strategic_context"] += f"\n\n# {current_section}\n{content_text}" if context_map["strategic_context"] else f"# {current_section}\n{content_text}"
        
        # Clean up empty sections
        for key in context_map:
            context_map[key] = context_map[key].strip()
        
        return context_map
    
    @staticmethod
    def parse_context_update(content: str, context_type: str = "strategic_context") -> str:
        """
        Parse context updates/notes from frontend
        
        Args:
            content: Additional context or notes from user
            context_type: Which context type to update (default: strategic_context)
            
        Returns:
            Formatted content ready for storage
        """
        # Simple formatting for user notes/updates
        formatted_content = content.strip()
        
        # Add timestamp header for tracking
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if formatted_content:
            formatted_content = f"UPDATE ({timestamp}):\n{formatted_content}"
        
        return formatted_content
    
    @staticmethod
    def get_context_preview(content: str, max_length: int = 200) -> str:
        """
        Generate a preview of context content for UI display
        
        Args:
            content: Full context content
            max_length: Maximum length of preview
            
        Returns:
            Truncated preview with ellipsis if needed
        """
        if len(content) <= max_length:
            return content
        
        # Try to break at a sentence or paragraph boundary
        preview = content[:max_length]
        
        # Find the last sentence or paragraph break
        for break_char in ['\n\n', '. ', '.\n']:
            last_break = preview.rfind(break_char)
            if last_break > max_length * 0.7:  # At least 70% of desired length
                return preview[:last_break + len(break_char)] + "..."
        
        # If no good break point, just truncate with ellipsis
        return preview + "..."

# Singleton service instance
def get_context_parser() -> ContextParser:
    """Get the context parser service instance"""
    return ContextParser() 