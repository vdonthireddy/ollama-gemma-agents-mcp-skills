import os
from pathlib import Path
from typing import Dict
from fastmcp import FastMCP
from mcp_skills.config import Settings, settings
from mcp_skills.server.tools import default_registry
from mcp_skills.server.skills import load_skills, Skill

def build_server(config_settings: Settings = settings) -> FastMCP:
    mcp = FastMCP("mcp-skills")
    
    # Register built-in tools from registry
    for name, tool in default_registry.tools.items():
        # Ensure name and description match
        mcp.tool(name=name, description=tool.description)(tool.fn)
        
    # Load skills
    skills_map = load_skills(config_settings.skills_dir)
    
    # Register each skill as a prompt
    for skill in skills_map.values():
        def make_prompt_fn(instructions: str):
            def prompt_fn() -> str:
                return instructions
            return prompt_fn
        
        mcp.prompt(
            name=skill.name,
            description=skill.description
        )(make_prompt_fn(skill.instructions))
        
    # Register list_skills tool
    @mcp.tool(name="list_skills", description="List all available skills (name and description).")
    def list_skills() -> list[dict[str, str]]:
        return [{"name": s.name, "description": s.description} for s in skills_map.values()]
        
    # Register load_skill tool
    @mcp.tool(name="load_skill", description="Load the full instruction set for a specific skill by name.")
    def load_skill(name: str) -> str:
        skill = skills_map.get(name)
        if not skill:
            return f"Skill '{name}' not found."
        return skill.instructions
        
    return mcp
