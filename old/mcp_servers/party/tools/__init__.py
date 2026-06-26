from .invite_guests import SCHEMA as invite_guests_schema, handler as invite_guests_handler
from .budget_expenses import SCHEMA as budget_expenses_schema, handler as budget_expenses_handler
from .book_venue import SCHEMA as book_venue_schema, handler as book_venue_handler
from .order_cake import SCHEMA as order_cake_schema, handler as order_cake_handler
from .hire_entertainment import SCHEMA as hire_entertainment_schema, handler as hire_entertainment_handler
from .buy_decorations import SCHEMA as buy_decorations_schema, handler as buy_decorations_handler
from .send_reminders import SCHEMA as send_reminders_schema, handler as send_reminders_handler

TOOLS = [
    invite_guests_schema,
    budget_expenses_schema,
    book_venue_schema,
    order_cake_schema,
    hire_entertainment_schema,
    buy_decorations_schema,
    send_reminders_schema
]

TOOL_REGISTRY = {
    "invite_guests": invite_guests_handler,
    "budget_expenses": budget_expenses_handler,
    "book_venue": book_venue_handler,
    "order_cake": order_cake_handler,
    "hire_entertainment": hire_entertainment_handler,
    "buy_decorations": buy_decorations_handler,
    "send_reminders": send_reminders_handler
}
