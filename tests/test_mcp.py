import unittest
import sys
import os
import asyncio
import json

# Append project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.travel.mcp_server_travel import mcp as travel_mcp
from mcp_servers.party.mcp_server_party import mcp as party_mcp

class TestMcpRegistry(unittest.TestCase):
    def test_travel_mcp_registration(self):
        # Retrieve tools registered via fastmcp instance using list_tools coroutine
        tools = asyncio.run(travel_mcp.list_tools())
        tool_names = [t.name for t in tools]
        expected_tools = [
            "search_flights", "book_flight", "search_hotels",
            "book_hotel", "rent_car", "book_attraction", "generate_travel_itinerary"
        ]
        for t in expected_tools:
            self.assertIn(t, tool_names, f"Tool {t} not found in travel MCP server")

    def test_travel_mcp_resources(self):
        # Verify that skills://list resource is registered
        resources = asyncio.run(travel_mcp.list_resources())
        resource_uris = [str(r.uri) for r in resources]
        self.assertIn("skills://list", resource_uris)

        # Verify reading the resource returns skills json
        res = asyncio.run(travel_mcp.read_resource("skills://list"))
        self.assertTrue(len(res.contents) > 0)
        skills = json.loads(res.contents[0].content)
        self.assertTrue(isinstance(skills, list))
        self.assertEqual(len(skills), 3)
        self.assertEqual(skills[0]["id"], "full_vacation_planner")

    def test_party_mcp_registration(self):
        tools = asyncio.run(party_mcp.list_tools())
        tool_names = [t.name for t in tools]
        expected_tools = [
            "invite_guests", "budget_expenses", "book_venue",
            "order_cake", "hire_entertainment", "buy_decorations", "send_reminders"
        ]
        for t in expected_tools:
            self.assertIn(t, tool_names, f"Tool {t} not found in party MCP server")

    def test_party_mcp_resources(self):
        # Verify that skills://list resource is registered
        resources = asyncio.run(party_mcp.list_resources())
        resource_uris = [str(r.uri) for r in resources]
        self.assertIn("skills://list", resource_uris)

        # Verify reading the resource returns skills json
        res = asyncio.run(party_mcp.read_resource("skills://list"))
        self.assertTrue(len(res.contents) > 0)
        skills = json.loads(res.contents[0].content)
        self.assertTrue(isinstance(skills, list))
        self.assertEqual(len(skills), 3)
        self.assertEqual(skills[0]["id"], "core_event_planning")

if __name__ == "__main__":
    import json
    unittest.main()
