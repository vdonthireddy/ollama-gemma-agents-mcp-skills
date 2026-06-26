import pytest
from mcp_skills.agent.agent import Agent
from mcp_skills.llm.dummy import DummyClient
from mcp_skills.llm.base import LLMReply, ToolCall

class MockMCPClient:
    def __init__(self):
        self.tools_listed = False
        self.calls = []

    async def list_tool_specs(self):
        self.tools_listed = True
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Evaluate basic arithmetic",
                    "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}}
                }
            }
        ]

    async def call_tool(self, name: str, arguments: dict):
        self.calls.append((name, arguments))
        if name == "calculator":
            return '{"expression": "6 * 7", "result": 42.0}'
        return "mock result"

@pytest.mark.asyncio
async def test_agent_loop_runs_tool():
    script = [
        LLMReply(tool_calls=[ToolCall(name="calculator", arguments={"expression": "6 * 7"}, id="call1")]),
        LLMReply(content="The answer is 42.0")
    ]
    llm = DummyClient(script=script)
    mcp = MockMCPClient()
    agent = Agent(llm, mcp)
    
    result = await agent.run("what is 6 * 7?")
    assert result.answer == "The answer is 42.0"
    assert len(result.invocations) == 1
    assert result.invocations[0].tool_name == "calculator"
    assert result.invocations[0].arguments == {"expression": "6 * 7"}
    assert result.steps == 2

@pytest.mark.asyncio
async def test_agent_max_steps_limit():
    # Loop indefinitely requesting calculator tool call
    script = [
        LLMReply(tool_calls=[ToolCall(name="calculator", arguments={"expression": "1+1"}, id="call1")])
    ] * 5
    llm = DummyClient(script=script)
    mcp = MockMCPClient()
    agent = Agent(llm, mcp)
    
    result = await agent.run("what is 1+1?", max_steps=3)
    assert result.status == "limit_reached"
    assert result.steps == 3
    assert len(result.invocations) == 3

class ErrorMockMCPClient(MockMCPClient):
    async def call_tool(self, name: str, arguments: dict):
        raise ValueError("Failed to call tool")

@pytest.mark.asyncio
async def test_agent_tool_error_handling():
    script = [
        LLMReply(tool_calls=[ToolCall(name="calculator", arguments={"expression": "1+1"}, id="call1")]),
        LLMReply(content="The tool failed")
    ]
    llm = DummyClient(script=script)
    mcp = ErrorMockMCPClient()
    agent = Agent(llm, mcp)
    
    result = await agent.run("what is 1+1?")
    assert result.answer == "The tool failed"
    assert len(result.invocations) == 1
    assert "Error calling tool" in result.invocations[0].result

