"""
Template Resource Example: User Info

Demonstrates a dynamic resource template with:
- Path parameters: {user_id}
- Query parameters: {?format}
- Multiple output formats (json, xml, text)
- Optional logging for access tracking
"""

import json
from fastmcp import Context


async def get_user_info(
    user_id: str, format: str = "json", ctx: Context | None = None
) -> str:
    """
    Get user information in different formats

    This is a template resource example that demonstrates:
    - Path parameters: {user_id}
    - Query parameters: {?format}
    - Multiple output formats
    - Optional context usage for logging

    URI Pattern: userinfo://{user_id}{?format}

    Args:
        user_id: The user ID to lookup (path parameter)
        format: Output format - json, xml, or text (query parameter, default: json)
        ctx: Optional FastMCP context for logging

    Returns:
        User information in requested format

    Examples:
        userinfo://123           → JSON format (default)
        userinfo://456?format=xml  → XML format
        userinfo://789?format=text → Plain text format

    Note:
        This uses mock data for demonstration. In production,
        you would fetch real user data from a database or API.
    """

    # Optional: Log resource access if context available
    if ctx:
        await ctx.debug(f"Resource access: userinfo://{user_id}?format={format}")

    # Mock user data (in production, fetch from database/API)
    user_data = {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-10-26T10:00:00Z",
    }

    # Format output based on query parameter
    if format == "xml":
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<user>
    <id>{user_data["user_id"]}</id>
    <name>{user_data["name"]}</name>
    <email>{user_data["email"]}</email>
    <status>{user_data["status"]}</status>
    <created_at>{user_data["created_at"]}</created_at>
    <last_login>{user_data["last_login"]}</last_login>
</user>"""

    elif format == "text":
        return f"""User Information
================
ID: {user_data["user_id"]}
Name: {user_data["name"]}
Email: {user_data["email"]}
Status: {user_data["status"]}
Created: {user_data["created_at"]}
Last Login: {user_data["last_login"]}"""

    else:  # json (default)
        return json.dumps(user_data, indent=2)
