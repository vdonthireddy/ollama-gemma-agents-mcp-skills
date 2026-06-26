import tempfile
from pathlib import Path
from mcp_skills.server.skills.loader import load_skills, parse_skill_file

def test_parse_valid_skill():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill description
---
# Test Skill
These are the instructions.""")
        
        skill = parse_skill_file(skill_file)
        assert skill.name == "test-skill"
        assert skill.description == "A test skill description"
        assert skill.instructions == "# Test Skill\nThese are the instructions."
        assert skill.scripts_path is None

def test_load_skills_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "skill-1").mkdir()
        (p / "skill-1" / "SKILL.md").write_text("""---
name: skill-1
description: Desc 1
---
Instructions 1""")
        
        (p / "skill-2").mkdir()
        (p / "skill-2" / "SKILL.md").write_text("""---
name: skill-2
description: Desc 2
---
Instructions 2""")
        skills = load_skills(tmpdir)
        assert len(skills) == 2
        assert "skill-1" in skills
        assert "skill-2" in skills
        assert skills["skill-1"].description == "Desc 1"
        assert skills["skill-2"].instructions == "Instructions 2"

def test_parse_malformed_skill_no_frontmatter():
    import pytest
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("no frontmatter delimiters here")
        
        with pytest.raises(ValueError, match="missing frontmatter boundaries"):
            parse_skill_file(skill_file)

def test_parse_malformed_skill_missing_fields():
    import pytest
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
---
missing description""")
        
        with pytest.raises(ValueError, match="must define 'name' and 'description'"):
            parse_skill_file(skill_file)

