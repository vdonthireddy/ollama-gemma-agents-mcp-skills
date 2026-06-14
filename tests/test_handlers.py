import unittest
import sys
import os

# Append project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.travel.tools.search_flights import handler as search_flights_handler
from mcp_servers.travel.tools.book_flight import handler as book_flight_handler
from mcp_servers.travel.tools.search_hotels import handler as search_hotels_handler
from mcp_servers.travel.tools.book_hotel import handler as book_hotel_handler
from mcp_servers.travel.tools.rent_car import handler as rent_car_handler
from mcp_servers.travel.tools.book_attraction import handler as book_attraction_handler
from mcp_servers.travel.tools.generate_travel_itinerary import handler as generate_travel_itinerary_handler

from mcp_servers.party.tools.invite_guests import handler as invite_guests_handler
from mcp_servers.party.tools.budget_expenses import handler as budget_expenses_handler
from mcp_servers.party.tools.book_venue import handler as book_venue_handler
from mcp_servers.party.tools.order_cake import handler as order_cake_handler
from mcp_servers.party.tools.hire_entertainment import handler as hire_entertainment_handler
from mcp_servers.party.tools.buy_decorations import handler as buy_decorations_handler
from mcp_servers.party.tools.send_reminders import handler as send_reminders_handler

class TestHandlers(unittest.TestCase):
    # --- Travel Handlers ---
    def test_search_flights(self):
        res = search_flights_handler("JFK", "CDG", "2026-08-10")
        self.assertIn("flights", res)
        self.assertTrue(len(res["flights"]) > 0)
        self.assertIn("content", res)

    def test_book_flight(self):
        res = book_flight_handler("FL-101")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["status"], "confirmed")
        self.assertEqual(res["booking"]["flight_id"], "FL-101")

    def test_search_hotels(self):
        res = search_hotels_handler("Paris", 250)
        self.assertIn("hotels", res)
        self.assertTrue(len(res["hotels"]) > 0)

    def test_book_hotel(self):
        res = book_hotel_handler("Hotel Ritz", 3)
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["hotel_name"], "Hotel Ritz")
        self.assertEqual(res["booking"]["nights"], 3)

    def test_rent_car(self):
        res = rent_car_handler("Tokyo", "SUV")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["car_type"], "SUV")

    def test_book_attraction(self):
        res = book_attraction_handler("London", "London Eye")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["activity"], "London Eye")

    def test_generate_travel_itinerary(self):
        bookings = [
            {"booking_type": "flight", "flight_id": "FL-101", "booking_code": "XYZ123"},
            {"booking_type": "hotel", "hotel_name": "Hotel Ritz", "reservation_code": "HOTEL789", "nights": 3}
        ]
        res = generate_travel_itinerary_handler(bookings)
        self.assertIn("itinerary_text", res)
        self.assertIn("YOUR TRAVEL ITINERARY", res["itinerary_text"])

    # --- Party Handlers ---
    def test_invite_guests(self):
        res = invite_guests_handler(["Alice", "Bob", "Charlie"])
        self.assertIn("rsvp_count", res)
        self.assertTrue(res["rsvp_count"] >= 1)

    def test_budget_expenses(self):
        res = budget_expenses_handler(10)
        self.assertIn("budget", res)
        self.assertEqual(res["budget"]["rsvp_count"], 10)
        self.assertTrue(res["budget"]["total_estimated_cost"] > 0)

    def test_book_venue(self):
        res = book_venue_handler("Cozy Club", 15)
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["venue_name"], "Cozy Club")

    def test_order_cake(self):
        res = order_cake_handler("Red Velvet", "Medium 10-inch", "Happy Birthday!")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["flavor"], "Red Velvet")

    def test_hire_entertainment(self):
        res = hire_entertainment_handler("DJ")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["type"], "DJ")

    def test_buy_decorations(self):
        res = buy_decorations_handler("Neon")
        self.assertIn("booking", res)
        self.assertEqual(res["booking"]["theme"], "Neon")

    def test_send_reminders(self):
        res = send_reminders_handler(["alice@test.com", "bob@test.com"], "Cozy Club")
        self.assertEqual(res["status"], "reminders_sent")
        self.assertEqual(res["emails_sent_count"], 2)

if __name__ == "__main__":
    unittest.main()
