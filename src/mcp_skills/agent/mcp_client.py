import sys
import os
from contextlib import AsyncExitStack
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self, command: str = sys.executable, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args or ["-m", "mcp_skills.server"]
        self.env = env or {**os.environ}
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None

    async def __aenter__(self):
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env
        )
        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tool_specs(self) -> List[Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("MCPClient not initialized. Use inside async with block.")
            
        mcp_tools_res = await self.session.list_tools()
        openai_tools = []
        for t in mcp_tools_res.tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema or {"type": "object", "properties": {}}
                }
            })
        return openai_tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        if not self.session:
            raise RuntimeError("MCPClient not initialized. Use inside async with block.")
        res = await self.session.call_tool(name, arguments)
        texts = []
        for content in res.content:
            if hasattr(content, "text"):
                texts.append(content.text)
        return "\n".join(texts)
