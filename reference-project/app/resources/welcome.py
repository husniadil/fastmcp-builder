"""
Dynamic Resource Example: Welcome Message

Demonstrates a function-based resource with static content.
This is registered as a dynamic resource (function-based) but returns
constant content, making it behave like a static resource.

Note: FastMCP has two resource types:
- Static resources: Class-based (TextResource, FileResource)
- Dynamic resources: Function-based (like this one)
"""

from app.config import Config


def get_welcome_message() -> str:
    """
    Welcome message resource

    This is a dynamic (function-based) resource with static content that:
    - Has a fixed URI: greeting://welcome
    - Returns constant content
    - Provides server information

    URI: greeting://welcome

    Returns:
        Welcome message with server info

    Example:
        Access via: greeting://welcome
        Returns: "Welcome to MCP Auth Demo! ..."
    """
    return f"""Welcome to {Config.SERVER_NAME}! 🎉

This is a minimalist MCP server demonstrating:
✅ Google OAuth 2.0 authentication
✅ Basic and advanced tools
✅ Static and template resources
✅ Reusable prompts
✅ Advanced FastMCP features

Server Version: {Config.SERVER_VERSION}
Base URL: {Config.BASE_URL}

Get started by exploring available tools and resources!
"""
