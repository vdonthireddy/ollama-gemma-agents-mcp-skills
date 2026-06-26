import json
import re
from typing import List, Dict, Any, Optional
from mcp_skills.llm.base import LLMClient, LLMReply, ToolCall

class DummyClient(LLMClient):
    def __init__(self, script: Optional[List[LLMReply]] = None):
        self.script = script or []
        self.call_count = 0

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMReply:
        # If we have a scripted response, use it
        if self.call_count < len(self.script):
            reply = self.script[self.call_count]
            self.call_count += 1
            return reply

        # Retrieve the user task
        user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        
        # Retrieve the list of tool results
        tool_results = [m for m in messages if m["role"] == "tool"]
        tool_names_called = [m["name"] for m in tool_results]
        
        # Rule 1: arithmetic in task & calculator not yet called
        # Check if the user message contains numbers and math operators
        has_arithmetic = any(char in user_message for char in "+-*/%*") or "multiply" in user_message or "calculator" in user_message
        if has_arithmetic and "calculator" not in tool_names_called:
            # Extract basic expression or default to 6 * 7
            expression = "6 * 7"
            match = re.search(r'[\d\s\+\-\*\/\%\(\)\.\*]+', user_message)
            if match:
                expr_cand = match.group(0).strip()
                if any(op in expr_cand for op in "+-*/"):
                    expression = expr_cand
            return LLMReply(
                tool_calls=[ToolCall(
                    name="calculator",
                    arguments={"expression": expression},
                    id="call_calc_dummy"
                )]
            )
            
        # Rule 2: task mentions 'skill' & list_skills not yet called
        has_skill_mention = "skill" in user_message.lower() or "skills" in user_message.lower()
        if has_skill_mention and "list_skills" not in tool_names_called:
            return LLMReply(
                tool_calls=[ToolCall(
                    name="list_skills",
                    arguments={},
                    id="call_list_skills_dummy"
                )]
            )
            
        # If list_skills was called and the user asks for a skill detail but load_skill hasn't been called
        if "list_skills" in tool_names_called and "load_skill" not in tool_names_called:
            # Check if there is a skill list result to parse
            skill_name = "pirate-speak"
            list_skills_msg = next((m for m in tool_results if m["name"] == "list_skills"), None)
            if list_skills_msg:
                try:
                    skills = json.loads(list_skills_msg["content"])
                    if isinstance(skills, list) and len(skills) > 0:
                        skill_name = skills[0].get("name", "pirate-speak")
                except Exception:
                    pass
            return LLMReply(
                tool_calls=[ToolCall(
                    name="load_skill",
                    arguments={"name": skill_name},
                    id="call_load_skill_dummy"
                )]
            )

        # Rule 3: final answer (summarize last tool result)
        if tool_results:
            last_result = tool_results[-1]
            content_str = last_result["content"]
            try:
                data = json.loads(content_str)
                if isinstance(data, dict) and "result" in data:
                    return LLMReply(content=f"The answer is {data['result']}")
                elif isinstance(data, list):
                    skills_str = ", ".join([s.get("name", "") for s in data])
                    return LLMReply(content=f"The available skills are: {skills_str}")
                else:
                    return LLMReply(content=f"Here is the result: {content_str}")
            except Exception:
                # Raw string (like skill instructions)
                if last_result["name"] == "load_skill":
                    return LLMReply(content=f"Loaded skill instructions:\n\n{content_str}")
                return LLMReply(content=f"The answer is {content_str}")
                
        return LLMReply(content="Hello! I am the dummy agent. How can I help you?")
