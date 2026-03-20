# LMS Telegram Bot — Development Plan

## Overview

This document outlines the plan for building a Telegram bot that lets users interact with the LMS backend through chat. The bot will support slash commands (`/start`, `/help`, `/health`, `/labs`, `/scores`) and understand plain language questions using an LLM for intent routing.

## Architecture

### Handler Separation Pattern

The core architectural decision is **separation of concerns**: handlers are pure functions that take input and return text. They don't depend on Telegram. This means:

- The same handler works from `--test` mode, unit tests, or the actual Telegram bot
- Testing doesn't require a Telegram connection
- Logic is isolated from transport layer (Telegram API)

### Layered Structure

```
bot/
├── bot.py          # Entry point: Telegram startup + --test mode
├── handlers/       # Command handlers (no Telegram dependency)
├── services/       # API client, LLM client
├── config.py       # Environment variable loading
└── pyproject.toml  # Dependencies
```

## Task 1: Plan and Scaffold (Current)

**Goal:** Create project structure with testable handlers.

- [x] Create `bot/` directory structure
- [x] Implement `bot.py` with `--test` mode
- [x] Create handler module with placeholder functions
- [x] Set up `pyproject.toml` with dependencies
- [ ] Create `.env.bot.secret` with real credentials
- [ ] Verify all commands work in test mode

**Acceptance:** `uv run bot.py --test "/start"` prints welcome message and exits 0.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend.

- Create `services/lms_api.py` — HTTP client with Bearer token auth
- Implement `/health` — call `GET /health` on backend, report up/down
- Implement `/labs` — call `GET /items?category=lab`, format list
- Implement `/scores <lab>` — call `GET /analytics/lab/<lab_id>`, show pass rates
- Add error handling — friendly messages when backend is down

**Pattern:** API client reads `LMS_API_URL` and `LMS_API_KEY` from environment. All requests include `Authorization: Bearer <key>`.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Let users ask questions in plain language.

- Create `services/llm_client.py` — wrapper around LLM API
- Define tools for each backend endpoint (e.g., `get_labs()`, `get_scores(lab_id)`)
- Implement intent router: user text → LLM → tool call → API → response
- Add inline keyboard buttons for common actions

**Key insight:** The LLM reads tool descriptions to decide which to call. Description quality matters more than prompt engineering. If the LLM picks the wrong tool, improve the description — don't add regex routing.

## Task 4: Containerize and Deploy

**Goal:** Deploy bot alongside backend on VM.

- Create `bot/Dockerfile` — minimal Python image, copy bot code
- Add bot service to `docker-compose.yml`
- Configure Docker networking — containers use service names, not `localhost`
- Document deployment in README

**Docker networking:** Inside containers, `LMS_API_URL` should be `http://backend:42002` (service name), not `localhost`.

## Testing Strategy

1. **Unit tests** — test handlers in isolation (pytest)
2. **Test mode** — `--test` flag for manual verification
3. **Integration tests** — verify backend calls work (requires running backend)
4. **Live testing** — deploy to VM and test in Telegram

## Deployment Checklist

- [ ] `.env.bot.secret` on VM with real `BOT_TOKEN`
- [ ] Backend running and accessible
- [ ] Bot container builds successfully
- [ ] `docker-compose up -d` starts all services
- [ ] Bot responds to `/start` in Telegram

## Future Improvements (P2/P3)

- Response caching to reduce API calls
- Conversation context for multi-turn dialogues
- Rich formatting (tables, charts as images)
- Analytics on user queries
