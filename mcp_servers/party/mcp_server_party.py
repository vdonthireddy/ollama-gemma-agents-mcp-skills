import os
import sys
import json

# Add local tools directory and project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from fastmcp import FastMCP
from mcp_servers.party.tools.invite_guests import handler as invite_guests_handler
from mcp_servers.party.tools.budget_expenses import handler as budget_expenses_handler
from mcp_servers.party.tools.book_venue import handler as book_venue_handler
from mcp_servers.party.tools.order_cake import handler as order_cake_handler
from mcp_servers.party.tools.hire_entertainment import handler as hire_entertainment_handler
from mcp_servers.party.tools.buy_decorations import handler as buy_decorations_handler
from mcp_servers.party.tools.send_reminders import handler as send_reminders_handler

# Initialize the FastMCP server
mcp = FastMCP("GemmaJnana Party Tools Server")

# Read session name from environment
SESSION_NAME = os.getenv("SESSION_NAME", "default")

@mcp.tool()
def invite_guests(guest_names: list) -> str:
    """Send invitations to a list of guests and receive confirmation count (RSVPs)."""
    result = invite_guests_handler(guest_names, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def budget_expenses(rsvp_count: int) -> str:
    """Estimate venues, catering, cake, and decoration costs based on RSVP count."""
    result = budget_expenses_handler(rsvp_count, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def book_venue(venue_name: str, guest_count: int) -> str:
    """Reserve a party venue space for a specific guest count."""
    result = book_venue_handler(venue_name, guest_count, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def order_cake(flavor: str, size: str, inscription: str) -> str:
    """Order a customized birthday cake with choice of flavor, size, and custom inscription."""
    result = order_cake_handler(flavor, size, inscription, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def hire_entertainment(type: str) -> str:
    """Book event entertainment service (e.g. DJ, Magician, Photobooth)."""
    result = hire_entertainment_handler(type, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def buy_decorations(theme: str) -> str:
    """Purchase themed decorations (balloons, plates, streamers) based on party theme."""
    result = buy_decorations_handler(theme, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def send_reminders(guest_emails: list, location: str) -> str:
    """Send email/SMS party reminder updates to all confirmed guests with location details."""
    result = send_reminders_handler(guest_emails, location, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.resource("skills://list", mime_type="application/json")
def list_skills() -> str:
    """List party planning skills available on this server."""
    skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
    skills_list = []
    if os.path.exists(skills_dir):
        try:
            for file in sorted(os.listdir(skills_dir)):
                if file.endswith(".json"):
                    with open(os.path.join(skills_dir, file), "r") as f:
                        skills_list.append(json.load(f))
        except Exception:
            pass
    return json.dumps(skills_list)

if __name__ == "__main__":
    host = os.getenv("PARTY_MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PARTY_MCP_PORT", "8002"))
    mcp.run(transport="sse", host=host, port=port)
