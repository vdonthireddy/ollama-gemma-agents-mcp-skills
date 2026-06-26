import asyncio
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from mcp_skills.agent.mcp_client import MCPClient
from mcp_skills.llm.base import LLMClient, LLMReply
from mcp_skills.agent.prompts import SYSTEM_PROMPT

@dataclass
class Invocation:
    tool_name: str
    arguments: Dict[str, Any]
    result: str

@dataclass
class AgentResult:
    answer: str
    invocations: List[Invocation] = field(default_factory=list)
    steps: int = 0
    status: str = "completed"

class Agent:
    def __init__(self, llm: LLMClient, mcp_client: MCPClient):
        self.llm = llm
        self.mcp_client = mcp_client

    async def run(self, task: str, max_steps: int = 12) -> AgentResult:
        # 1. Discover tools
        tools = await self.mcp_client.list_tool_specs()
        
        # 2. Seed the conversation
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ]
        
        invocations = []
        steps = 0
        answer = ""
        
        # 3. Loop
        while steps < max_steps:
            steps += 1
            # Run complete in a thread so sync network requests don't block the event loop
            reply = await asyncio.to_thread(self.llm.complete, messages, tools)
            
            # Check if LLM requested tool calls
            if reply.wants_tools:
                assistant_msg = {
                    "role": "assistant",
                    "content": reply.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments) if not isinstance(tc.arguments, str) else tc.arguments
                            }
                        } for tc in reply.tool_calls
                    ]
                }
                messages.append(assistant_msg)
                
                # Execute tool calls
                for tc in reply.tool_calls:
                    try:
                        result = await self.mcp_client.call_tool(tc.name, tc.arguments)
                    except Exception as e:
                        result = f"Error calling tool '{tc.name}': {e}"
                        
                    invocations.append(Invocation(
                        tool_name=tc.name,
                        arguments=tc.arguments,
                        result=result
                    ))
                    
                    messages.append({
                        "role": "tool",
                        "name": tc.name,
                        "tool_call_id": tc.id,
                        "content": result
                    })
            else:
                # Plain text response is the final answer
                answer = reply.content or ""
                break
        else:
            answer = "Loop limit reached. Final response was: " + (reply.content or "")
            
        return AgentResult(
            answer=answer,
            invocations=invocations,
            steps=steps,
            status="completed" if steps < max_steps else "limit_reached"
        )
