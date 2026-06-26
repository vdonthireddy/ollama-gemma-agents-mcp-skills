from .search_flights import SCHEMA as search_flights_schema, handler as search_flights_handler
from .book_flight import SCHEMA as book_flight_schema, handler as book_flight_handler
from .search_hotels import SCHEMA as search_hotels_schema, handler as search_hotels_handler
from .book_hotel import SCHEMA as book_hotel_schema, handler as book_hotel_handler
from .rent_car import SCHEMA as rent_car_schema, handler as rent_car_handler
from .book_attraction import SCHEMA as book_attraction_schema, handler as book_attraction_handler
from .generate_travel_itinerary import SCHEMA as generate_travel_itinerary_schema, handler as generate_travel_itinerary_handler

TOOLS = [
    search_flights_schema,
    book_flight_schema,
    search_hotels_schema,
    book_hotel_schema,
    rent_car_schema,
    book_attraction_schema,
    generate_travel_itinerary_schema
]

TOOL_REGISTRY = {
    "search_flights": search_flights_handler,
    "book_flight": book_flight_handler,
    "search_hotels": search_hotels_handler,
    "book_hotel": book_hotel_handler,
    "rent_car": rent_car_handler,
    "book_attraction": book_attraction_handler,
    "generate_travel_itinerary": generate_travel_itinerary_handler
}
