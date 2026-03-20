#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test mode: prints response to stdout
    uv run bot.py                   # Production: connects to Telegram
"""

import argparse
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from config import BOT_TOKEN
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map commands to handler functions
HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def process_command(command: str) -> str:
    """Route a command to its handler and return the response."""
    # Extract command name (first word)
    cmd_name = command.split()[0].lower()
    
    handler = HANDLERS.get(cmd_name)
    if handler:
        return handler(command)
    else:
        return f"Unknown command: {cmd_name}. Use /help to see available commands."


# Create bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handle /start command from Telegram."""
    response = handle_start()
    await message.answer(response)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command from Telegram."""
    response = handle_help()
    await message.answer(response)


@dp.message(Command("health"))
async def cmd_health(message: types.Message):
    """Handle /health command from Telegram."""
    response = handle_health()
    await message.answer(response)


@dp.message(Command("labs"))
async def cmd_labs(message: types.Message):
    """Handle /labs command from Telegram."""
    response = handle_labs()
    await message.answer(response)


@dp.message(Command("scores"))
async def cmd_scores(message: types.Message):
    """Handle /scores command from Telegram."""
    # Extract lab argument if provided
    args = message.text.split()[1:] if message.text else []
    lab_name = " ".join(args) if args else ""
    response = handle_scores(lab_name)
    await message.answer(response)


async def main():
    """Start the bot."""
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: process a command and print response to stdout",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly and print result
        response = process_command(args.test)
        print(response)
        sys.exit(0)
    else:
        # Production mode: start Telegram bot
        import asyncio
        asyncio.run(main())
