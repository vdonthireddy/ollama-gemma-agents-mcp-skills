import click
import asyncio
from mcp_skills.config import settings
from mcp_skills.llm import build_llm_client
from mcp_skills.agent.mcp_client import MCPClient
from mcp_skills.agent.agent import Agent
from mcp_skills.server.skills import load_skills
from mcp_skills.server.app import build_server

@click.group()
def main():
    """MCP Skills CLI - run agents and serve skills."""
    pass

@main.command(name="serve")
@click.option("--host", default=None, help="Host to bind to (if running over HTTP/SSE)")
@click.option("--port", default=None, type=int, help="Port to bind to")
def serve(host, port):
    """Start the MCP server on stdio transport (default)."""
    mcp = build_server(settings)
    kwargs = {}
    if host:
        kwargs["host"] = host
    if port:
        kwargs["port"] = port
        kwargs["transport"] = "sse"
    mcp.run(**kwargs)

@main.command(name="run")
@click.argument("task")
def run(task):
    """Run the Agent on a specific task."""
    click.echo(f"LLM Provider: {settings.llm_provider}")
    click.echo(f"Model: {settings.model}")
    click.echo(f"Skills Dir: {settings.skills_dir}")
    click.echo("Starting agent loop...")
    
    async def _run():
        llm = build_llm_client(settings)
        async with MCPClient() as mcp_client:
            agent = Agent(llm, mcp_client)
            result = await agent.run(task)
            
            click.echo("\n--- Execution Trace ---")
            for i, inv in enumerate(result.invocations, 1):
                click.echo(f"Step {i}: Tool '{inv.tool_name}' called with {inv.arguments}")
                click.echo(f"Result {i}: {inv.result}")
                
            click.echo("\n--- Final Answer ---")
            click.echo(result.answer)
            click.echo(f"\nSteps taken: {result.steps} (Status: {result.status})")

    asyncio.run(_run())

@click.group(name="skills")
def skills_group():
    """Manage agent skills."""
    pass

@skills_group.command(name="list")
def list_skills_cmd():
    """List all discovered skills."""
    skills = load_skills(settings.skills_dir)
    if not skills:
        click.echo(f"No skills found in {settings.skills_dir}")
        return
    click.echo(f"Discovered skills in {settings.skills_dir}:")
    for name, skill in skills.items():
        click.echo(f"- {name}: {skill.description}")

main.add_command(skills_group)

if __name__ == "__main__":
    main()
