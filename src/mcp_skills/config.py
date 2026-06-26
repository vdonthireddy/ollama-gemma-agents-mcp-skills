import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

class Settings:
    def __init__(self):
        self.llm_provider = os.getenv("MCP_SKILLS_LLM_PROVIDER", "dummy").lower()
        self.model = os.getenv("MCP_SKILLS_MODEL", "gpt-4o-mini")
        self.openai_api_key = os.getenv("MCP_SKILLS_OPENAI_API_KEY", "")
        self.openai_base_url = os.getenv("MCP_SKILLS_OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # Default skills directory to the workspace root's skills/ directory
        default_skills_dir = Path(__file__).resolve().parents[2] / "skills"
        env_skills_dir = os.getenv("MCP_SKILLS_SKILLS_DIR")
        self.skills_dir = Path(env_skills_dir) if env_skills_dir else default_skills_dir

settings = Settings()
