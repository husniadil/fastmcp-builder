#!/usr/bin/env python3
"""
Complete FastMCP Server Structure Example

Demonstrates recommended project structure in a single file for reference.
Shows patterns for:
- Tools with different patterns
- Resources (static, dynamic, template, wildcard)
- Prompts
- Context usage
- OAuth setup (commented out - uncomment for production)

This is a reference implementation. For real projects, split into
app/tools/, app/resources/, app/prompts/ directories.

Run without OAuth:
    python complete_server_structure.py

Run with HTTP (no OAuth):
    python complete_server_structure.py --http

Run with OAuth:
    1. Uncomment OAuth section
    2. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
    3. python complete_server_structure.py --http --base-url https://your-ngrok-url.ngrok-free.app
"""

import os
import sys
import asyncio
from datetime import datetime, timezone
from urllib.parse import urlparse
from fastmcp import FastMCP, Context
from fastmcp.resources import TextResource

# from fastmcp.server.auth.providers.google import GoogleProvider  # Uncomment for OAuth
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVER_NAME = "Complete FastMCP Example"
SERVER_VERSION = "1.0.0"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


# ============================================================================
# CREATE SERVER
# ============================================================================

# Without OAuth (default for local testing)
mcp = FastMCP(SERVER_NAME)

# With OAuth (uncomment to enable)
# auth = GoogleProvider(
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     base_url=BASE_URL,
#     required_scopes=["openid", "email", "profile"],
#     redirect_path="/auth/callback",
# )
# mcp = FastMCP(SERVER_NAME, auth=auth)


# ============================================================================
# TOOLS - Different Patterns
# ============================================================================


# Pattern 1: Basic synchronous tool
@mcp.tool()
def ping() -> dict:
    """Health check - returns server status"""
    return {
        "status": "ok",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Pattern 2: Simple data processing
@mcp.tool()
def count_words(text: str) -> dict:
    """Count words in text"""
    words = text.split()
    return {
        "text_length": len(text),
        "word_count": len(words),
        "words": words,
    }


# Pattern 3: Async tool with Context (logging + progress)
@mcp.tool()
async def process_text(content: str, ctx: Context | None = None) -> dict:
    """Process text with logging and progress tracking"""
    if ctx:
        await ctx.info(f"📄 Processing {len(content)} characters")

    # Simulate multi-step processing
    steps = ["Tokenizing", "Analyzing", "Formatting"]

    for i, step in enumerate(steps):
        if ctx:
            await ctx.report_progress(i, len(steps), f"{step}...")
        await asyncio.sleep(0.1)  # Simulate work

    if ctx:
        await ctx.report_progress(len(steps), len(steps), "Complete!")
        await ctx.info("✅ Processing completed")

    return {
        "status": "completed",
        "character_count": len(content),
        "word_count": len(content.split()),
    }


# Pattern 4: Stateful tool (module-level state)
_counter = 0


@mcp.tool()
async def counter(action: str = "get", ctx: Context | None = None) -> dict:
    """
    Manage a counter

    Args:
        action: "get", "increment", "decrement", or "reset"

    ⚠️ Note: Uses module-level state (resets on restart)
    """
    global _counter

    if action == "increment":
        _counter += 1
    elif action == "decrement":
        _counter -= 1
    elif action == "reset":
        _counter = 0

    if ctx:
        await ctx.info(f"Counter: {_counter} (action: {action})")

    return {"count": _counter, "action": action}


# ============================================================================
# RESOURCES - Different Types
# ============================================================================

# Static resource (TextResource)
status_resource = TextResource(
    uri="text://status",
    text="🟢 Server is operational",
    name="Server Status",
    description="Current server status",
    mime_type="text/plain",
)


@mcp.resource("text://status")
def get_status():
    """Static text resource"""
    return status_resource.text


# Dynamic resource (function-based)
@mcp.resource("greeting://welcome")
def get_welcome() -> str:
    """Welcome message"""
    return f"""Welcome to {SERVER_NAME}!

Version: {SERVER_VERSION}
Status: Running
Time: {datetime.now(timezone.utc).isoformat()}

Available tools:
- ping: Health check
- count_words: Count words in text
- process_text: Process text with progress
- counter: Manage counter

Try calling a tool to get started!
"""


# Template resource (with path parameter)
@mcp.resource("user://{user_id}")
async def get_user_info(user_id: str, ctx: Context | None = None) -> str:
    """
    Get user information

    Args:
        user_id: User ID to lookup

    Example URIs:
        user://123
        user://abc
    """
    if ctx:
        await ctx.debug(f"Fetching user: {user_id}")

    # Mock user data
    return f"""User Information
================
ID: {user_id}
Name: User {user_id}
Email: user{user_id}@example.com
Status: Active
"""


# Wildcard resource (matches multiple segments)
@mcp.resource("docs://{path*}")
async def get_docs(path: str, ctx: Context | None = None) -> str:
    """
    Documentation pages

    Examples:
        docs://readme
        docs://api/tools
        docs://guides/setup
    """
    docs = {
        "readme": "# README\n\nThis is the main documentation.",
        "api/tools": "# API - Tools\n\nList of available tools...",
        "guides/setup": "# Setup Guide\n\nHow to set up the server...",
    }

    if path in docs:
        if ctx:
            await ctx.debug(f"✅ Found docs: {path}")
        return docs[path]

    # Not found
    available = "\n".join(f"- docs://{p}" for p in docs.keys())
    return f"Documentation not found: {path}\n\nAvailable:\n{available}"


# ============================================================================
# PROMPTS - Reusable Templates
# ============================================================================


@mcp.prompt()
def explain_concept(
    concept: str,
    audience_level: str = "intermediate",
    include_examples: bool = True,
) -> str:
    """
    Generate a prompt to explain a technical concept

    Args:
        concept: The concept to explain
        audience_level: "beginner", "intermediate", or "advanced"
        include_examples: Whether to include examples
    """
    prompt = f"Please explain '{concept}' for a {audience_level} audience.\n\n"

    if audience_level == "beginner":
        prompt += "Use simple language and avoid jargon. "
    elif audience_level == "advanced":
        prompt += "Include technical details and edge cases. "
    else:
        prompt += "Use technical terms but explain them clearly. "

    if include_examples:
        prompt += "\n\nPlease include practical examples."

    return prompt


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================


def run_server():
    """Run the server in STDIO or HTTP mode"""
    if "--http" in sys.argv:
        # HTTP mode
        print(f"🚀 Starting {SERVER_NAME} in HTTP mode")
        print(f"📍 Base URL: {BASE_URL}")
        print()

        parsed = urlparse(BASE_URL)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8000

        mcp.run(transport="http", host=host, port=port)
    else:
        # STDIO mode (default)
        print(f"🚀 Starting {SERVER_NAME} in STDIO mode")
        mcp.run()


if __name__ == "__main__":
    run_server()
