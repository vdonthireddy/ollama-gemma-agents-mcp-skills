from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    id: str

@dataclass
class LLMReply:
    content: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)

    @property
    def wants_tools(self) -> bool:
        return len(self.tool_calls) > 0

class LLMClient:
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMReply:
        raise NotImplementedError
