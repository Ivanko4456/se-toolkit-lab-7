"""
Command handlers for the LMS Telegram bot.

Handlers are pure functions: they take input and return text.
They don't know about Telegram — same function works from
--test mode, unit tests, or the actual Telegram bot.
"""

from services import LMSAPIError, get_health, get_items, get_pass_rates


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
    try:
        result = get_health()
        if result["healthy"]:
            return f"Backend is healthy. {result['item_count']} items available."
        else:
            return "Backend returned unhealthy status."
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


def handle_labs(user_input: str = "") -> str:
    """Handle /labs command - lists available labs."""
    try:
        items = get_items()
        # Filter for labs (type == "lab")
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "No labs found."
        
        lines = ["Available labs:"]
        for lab in labs:
            # Use 'title' field from the API response
            title = lab.get("title", "Unknown")
            lines.append(f"- {title}")
        
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {e.message}"


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command - shows per-task pass rates."""
    # Extract lab name from user_input
    # user_input contains everything after the command, e.g. "lab-04"
    lab_name = user_input.strip() if user_input else ""
    
    if not lab_name:
        return "Please specify a lab. Usage: /scores lab-04"
    
    try:
        pass_rates = get_pass_rates(lab_name)
        
        if not pass_rates:
            return f"No pass rate data found for '{lab_name}'."
        
        lines = [f"Pass rates for {lab_name}:"]
        for record in pass_rates:
            task_name = record.get("task", "Unknown task")
            avg_score = record.get("avg_score", 0)
            attempts = record.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except LMSAPIError as e:
        return f"Backend error: {e.message}"
