"""
Services layer for the bot.

Contains API clients (LMS, LLM) that handlers use to fetch data.
"""

from .lms_api import LMSAPIError, get_items, get_health, get_pass_rates
from .llm_client import route as llm_route

__all__ = [
    "LMSAPIError",
    "get_items",
    "get_health",
    "get_pass_rates",
    "llm_route",
]
