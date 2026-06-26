import os
from pathlib import Path
from typing import Dict
from mcp_skills.server.skills.models import Skill

def parse_skill_file(filepath: Path) -> Skill:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError("Invalid SKILL.md format: missing frontmatter boundaries ('---')")
    
    frontmatter_str = parts[1]
    instructions = "---".join(parts[2:]).strip()
    
    metadata = {}
    for line in frontmatter_str.strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip().lower()] = val.strip()
            
    name = metadata.get("name")
    description = metadata.get("description")
    if not name or not description:
        raise ValueError("SKILL.md must define 'name' and 'description' in frontmatter")
        
    scripts_dir = filepath.parent / "scripts"
    scripts_path = scripts_dir if scripts_dir.is_dir() else None
    
    return Skill(
        name=name,
        description=description,
        instructions=instructions,
        scripts_path=scripts_path
    )

def load_skills(skills_dir: str | Path) -> Dict[str, Skill]:
    skills_dir = Path(skills_dir)
    skills = {}
    if not skills_dir.exists():
        return skills
        
    for subfolder in skills_dir.iterdir():
        if subfolder.is_dir():
            skill_file = subfolder / "SKILL.md"
            if skill_file.exists():
                try:
                    skill = parse_skill_file(skill_file)
                    skills[skill.name] = skill
                except Exception as e:
                    print(f"Skipping malformed skill in {subfolder.name}: {e}")
                    
    return skills
