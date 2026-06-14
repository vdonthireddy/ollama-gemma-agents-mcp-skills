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
from mcp_servers.travel.tools.search_flights import handler as search_flights_handler
from mcp_servers.travel.tools.book_flight import handler as book_flight_handler
from mcp_servers.travel.tools.search_hotels import handler as search_hotels_handler
from mcp_servers.travel.tools.book_hotel import handler as book_hotel_handler
from mcp_servers.travel.tools.rent_car import handler as rent_car_handler
from mcp_servers.travel.tools.book_attraction import handler as book_attraction_handler
from mcp_servers.travel.tools.generate_travel_itinerary import handler as generate_travel_itinerary_handler

# Initialize the FastMCP server
mcp = FastMCP("GemmaJnana Tools Server")

# Read session name from environment
SESSION_NAME = os.getenv("SESSION_NAME", "default")

@mcp.tool()
def search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights between origin and destination on a specific date."""
    result = search_flights_handler(origin, destination, date, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def book_flight(flight_id: str) -> str:
    """Book a selected flight by ID and get a confirmation code."""
    result = book_flight_handler(flight_id, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def search_hotels(city: str, budget: float) -> str:
    """Find hotels in a city matching the specified maximum budget."""
    result = search_hotels_handler(city, budget, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def book_hotel(hotel_name: str, nights: int) -> str:
    """Book a room at a hotel for a specified number of nights."""
    result = book_hotel_handler(hotel_name, nights, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def rent_car(city: str, car_type: str) -> str:
    """Reserve a rental car of a specific type (e.g. SUV, Sedan) in a city."""
    result = rent_car_handler(city, car_type, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def book_attraction(city: str, activity: str) -> str:
    """Book a ticket for an attraction or activity in a target city."""
    result = book_attraction_handler(city, activity, session_name=SESSION_NAME)
    return json.dumps(result)

@mcp.tool()
def generate_travel_itinerary(bookings: list) -> str:
    """Compile all flight and accommodation bookings into a structured travel itinerary document."""
    result = generate_travel_itinerary_handler(bookings, session_name=SESSION_NAME)
    return json.dumps(result)

if __name__ == "__main__":
    mcp.run()
