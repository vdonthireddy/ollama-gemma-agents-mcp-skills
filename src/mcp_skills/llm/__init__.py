from mcp_skills.config import Settings
from mcp_skills.llm.base import LLMClient
from mcp_skills.llm.dummy import DummyClient
from mcp_skills.llm.openai_client import OpenAIClient

def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "openai":
        return OpenAIClient(settings)
    return DummyClient()
