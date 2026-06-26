import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from mcp_skills.llm.base import LLMClient, LLMReply, ToolCall
from mcp_skills.config import Settings

class OpenAIClient(LLMClient):
    def __init__(self, settings: Settings):
        self.client = OpenAI(
            api_key=settings.openai_api_key or "dummy_key",
            base_url=settings.openai_base_url
        )
        self.model = settings.model

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> LLMReply:
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message
        
        reply = LLMReply(content=message.content)
        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                reply.tool_calls.append(ToolCall(
                    name=tc.function.name,
                    arguments=args,
                    id=tc.id
                ))
        return reply
