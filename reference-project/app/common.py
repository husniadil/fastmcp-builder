"""
Common Registration Module

This module contains shared registration logic for both main.py and main_noauth.py
to eliminate code duplication and ensure consistency.

DRY principle: Don't Repeat Yourself
Any new tool, resource, or prompt should be registered here once.
"""

from fastmcp import FastMCP

# Tool imports
from app.tools.ping import ping
from app.tools.analyze_text import analyze_text
from app.tools.process_text import process_text
from app.tools.counter import counter
from app.tools.request_info import get_request_info
from app.tools.get_forecast import get_forecast

# Resource imports
from app.resources.welcome import get_welcome_message
from app.resources.userinfo import get_user_info
from app.resources.static import get_static_resources
from app.resources.docs import get_documentation

# Prompt imports
from app.prompts.explain import explain_concept


def register_all(mcp: FastMCP) -> None:
    """
    Register all tools, resources, and prompts to the FastMCP server instance

    Args:
        mcp: FastMCP server instance to register components to

    This function eliminates duplication between main.py and main_noauth.py
    by centralizing all registration logic in one place.
    """

    # ============================================================================
    # TOOLS - 6 production-ready tools
    # ============================================================================

    mcp.tool()(ping)  # Basic health check
    mcp.tool()(analyze_text)  # Simple text statistics
    mcp.tool()(process_text)  # Advanced text processor with logging
    mcp.tool()(counter)  # State management example
    mcp.tool()(get_request_info)  # Request metadata
    mcp.tool()(get_forecast)  # External API integration example

    # ============================================================================
    # RESOURCES - 4 types of resources
    # ============================================================================

    # Dynamic resources
    mcp.resource("greeting://welcome")(get_welcome_message)
    mcp.resource("userinfo://{user_id}")(get_user_info)

    # Wildcard resource
    mcp.resource("docs://{path*}")(get_documentation)

    # Static resources (class-based resources converted to function-based for registration)
    static_resources = get_static_resources()

    @mcp.resource("text://status")
    def get_status():
        return static_resources[0].text

    @mcp.resource("text://features")
    def get_features():
        return static_resources[1].text

    @mcp.resource("file://readme")
    def get_readme():
        return static_resources[2].path.read_text()

    # Conditional resource - only if test results file exists
    if len(static_resources) > 3:

        @mcp.resource("file://test-results")
        def get_test_results():
            return static_resources[3].path.read_text()

    # ============================================================================
    # PROMPTS - 1 universal prompt
    # ============================================================================

    mcp.prompt()(explain_concept)
