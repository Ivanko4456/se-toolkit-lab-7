"""
Configuration loader for the bot.

Reads secrets from .env.bot.secret (gitignored) and exposes them
as module-level variables. Uses python-dotenv to load .env files.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Find .env.bot.secret in the parent directory (repo root)
BOT_DIR = Path(__file__).parent
ROOT_DIR = BOT_DIR.parent
ENV_FILE = ROOT_DIR / ".env.bot.secret"

# Load environment variables from .env.bot.secret
load_dotenv(ENV_FILE)

# Expose configuration as module-level variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LMS_API_URL = os.getenv("LMS_API_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "coder-model")
