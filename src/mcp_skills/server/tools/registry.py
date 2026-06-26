from typing import Dict, Any, Callable
from mcp_skills.server.tools.base import Tool

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def tool(self, name: str, description: str, parameters: Dict[str, Any]):
        def decorator(fn: Callable[..., Any]):
            tool_obj = Tool(
                name=name,
                description=description,
                parameters=parameters,
                fn=fn
            )
            self.tools[name] = tool_obj
            return fn
        return decorator

default_registry = ToolRegistry()
