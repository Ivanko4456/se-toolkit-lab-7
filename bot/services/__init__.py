"""
Services layer for the bot.

Contains API clients (LMS, LLM) that handlers use to fetch data.
"""

from .lms_api import LMSAPIError, get_items, get_health, get_pass_rates

__all__ = ["LMSAPIError", "get_items", "get_health", "get_pass_rates"]
