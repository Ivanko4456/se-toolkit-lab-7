"""
Command handlers for the LMS Telegram bot.

Handlers are pure functions: they take input and return text.
They don't know about Telegram — same function works from
--test mode, unit tests, or the actual Telegram bot.
"""


def handle_start(user_input: str = "") -> str:
    """Handle /start command - returns welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help(user_input: str = "") -> str:
    """Handle /help command - lists available commands."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Show pass rates for a lab"
    )


def handle_health(user_input: str = "") -> str:
    """Handle /health command - checks backend status."""
    return "Not implemented yet"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - lists available labs."""
    return "Not implemented yet"


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - shows per-task pass rates."""
    return "Not implemented yet"
