from mcp_skills.llm.dummy import DummyClient
from mcp_skills.llm.base import LLMReply, ToolCall

def test_dummy_client_math_trigger():
    client = DummyClient()
    messages = [
        {"role": "user", "content": "What is 6 * 7?"}
    ]
    reply = client.complete(messages)
    assert reply.wants_tools
    assert reply.tool_calls[0].name == "calculator"
    assert reply.tool_calls[0].arguments == {"expression": "6 * 7"}

def test_dummy_client_skills_trigger():
    client = DummyClient()
    messages = [
        {"role": "user", "content": "What skills are available?"}
    ]
    reply = client.complete(messages)
    assert reply.wants_tools
    assert reply.tool_calls[0].name == "list_skills"

def test_dummy_client_scripted():
    scripted_reply = LLMReply(content="This is scripted")
    client = DummyClient(script=[scripted_reply])
    
    reply = client.complete([{"role": "user", "content": "Hello"}])
    assert reply.content == "This is scripted"
    assert not reply.wants_tools
