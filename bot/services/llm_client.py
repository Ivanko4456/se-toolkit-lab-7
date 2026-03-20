"""
LLM client for intent routing.

Sends user messages to the LLM with tool definitions.
The LLM decides which tools to call, and this client executes them.
"""

import json
import logging
import sys
from typing import Any

import httpx

from config import LLM_API_KEY, LLM_API_BASE_URL, LLM_API_MODEL
from .lms_api import (
    get_items,
    get_health,
    get_pass_rates,
    get_learners,
    get_scores,
    get_timeline,
    get_groups,
    get_top_learners,
    get_completion_rate,
    trigger_sync,
)

logger = logging.getLogger(__name__)

# Tool definitions for the LLM (9 tools as required)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this to find available labs.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab. Use this to show scores for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_health",
            "description": "Check if the backend is healthy and get item count.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use this to compare groups.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, default 5",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# Map tool names to functions
TOOL_FUNCTIONS = {
    "get_items": get_items,
    "get_pass_rates": lambda lab="": get_pass_rates(lab) if lab else get_pass_rates(""),
    "get_health": get_health,
    "get_learners": get_learners,
    "get_scores": lambda lab="": get_scores(lab) if lab else get_scores(""),
    "get_timeline": lambda lab="": get_timeline(lab) if lab else get_timeline(""),
    "get_groups": lambda lab="": get_groups(lab) if lab else get_groups(""),
    "get_top_learners": lambda lab="", limit=5: get_top_learners(lab, limit),
    "get_completion_rate": lambda lab="": get_completion_rate(lab) if lab else get_completion_rate(""),
    "trigger_sync": trigger_sync,
}

SYSTEM_PROMPT = """You are an LMS assistant bot. You help users get information about labs, tasks, and scores.

You have access to tools that fetch data from the LMS backend. When a user asks a question:
1. Think about what data you need
2. Call the appropriate tool(s)
3. Use the tool results to answer the user

If the user asks something you can't answer with your tools, say so politely and suggest what you CAN help with.

Available tools:
- get_items(): List all labs and tasks
- get_pass_rates(lab): Get scores for a specific lab
- get_health(): Check if backend is working
- get_learners(): List enrolled students
- get_scores(lab): Score distribution for a lab
- get_timeline(lab): Submissions per day
- get_groups(lab): Compare group performance
- get_top_learners(lab, limit): Top students leaderboard
- get_completion_rate(lab): Completion percentage
- trigger_sync(): Refresh data from autochecker

Always be helpful and concise. Use the data from tools to give specific answers with numbers."""


def call_llm(messages: list[dict]) -> dict:
    """
    Call the LLM API with messages and tool definitions.

    Args:
        messages: List of message dicts with 'role' and 'content'

    Returns:
        The LLM's response message dict
    """
    url = f"{LLM_API_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_API_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM HTTP error: {e.response.status_code} {e.response.text}")
        raise
    except httpx.ConnectError as e:
        logger.error(f"LLM connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise


def execute_tool(name: str, arguments: dict) -> Any:
    """
    Execute a tool function with the given arguments.

    Args:
        name: Tool name (e.g., "get_items")
        arguments: Dict of arguments to pass

    Returns:
        The tool's result
    """
    if name not in TOOL_FUNCTIONS:
        return f"Unknown tool: {name}"

    func = TOOL_FUNCTIONS[name]
    try:
        # Call function with arguments if provided
        if arguments:
            return func(**arguments)
        else:
            return func()
    except Exception as e:
        return f"Error executing {name}: {e}"


def route(user_message: str) -> str:
    """
    Route a user message through the LLM tool-calling loop.

    Args:
        user_message: The user's input text

    Returns:
        The final response to send to the user
    """
    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        try:
            response = call_llm(messages)
        except Exception as e:
            return f"LLM error: {e}. Try again later."

        # Check if LLM wants to call tools
        tool_calls = response.get("tool_calls", [])

        if not tool_calls:
            # LLM has final answer
            return response.get("content", "I don't have a response for that.")

        # Execute tools and collect results
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            # Debug output to stderr
            print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)

            result = execute_tool(tool_name, tool_args)

            # Debug output to stderr
            print(f"[tool] Result: {json.dumps(result) if isinstance(result, (dict, list)) else result}", file=sys.stderr)

            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
            })

        # Add LLM's tool call request to messages
        messages.append(response)

        # Add tool results to messages
        messages.extend(tool_results)

        print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)

    return "I'm having trouble processing your request. Please try again."
