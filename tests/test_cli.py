from click.testing import CliRunner
from mcp_skills.cli import main

def test_cli_skills_list():
    runner = CliRunner()
    result = runner.invoke(main, ["skills", "list"])
    assert result.exit_code == 0
    assert "Discovered skills" in result.output
    assert "pirate-speak" in result.output

def test_cli_run_agent():
    runner = CliRunner()
    result = runner.invoke(main, ["run", "what is 6 * 7?"])
    assert result.exit_code == 0
    assert "LLM Provider: dummy" in result.output
    assert "calculator" in result.output
    assert "42.0" in result.output
