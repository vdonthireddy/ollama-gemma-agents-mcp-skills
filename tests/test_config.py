import os
from mcp_skills.config import Settings

def test_config_defaults():
    settings = Settings()
    assert settings.llm_provider == "dummy"
    assert settings.model == "gpt-4o-mini"
    assert settings.openai_base_url == "https://api.openai.com/v1"

def test_config_env_override(monkeypatch):
    monkeypatch.setenv("MCP_SKILLS_LLM_PROVIDER", "openai")
    monkeypatch.setenv("MCP_SKILLS_MODEL", "gpt-4")
    monkeypatch.setenv("MCP_SKILLS_OPENAI_API_KEY", "test-key")
    
    settings = Settings()
    assert settings.llm_provider == "openai"
    assert settings.model == "gpt-4"
    assert settings.openai_api_key == "test-key"
