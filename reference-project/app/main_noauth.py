"""
MCP Auth Demo - No Auth Version (for local testing)

Same features as main.py but without OAuth for easier local testing.
Use this for STDIO mode with Claude Desktop.
"""

import sys
from urllib.parse import urlparse
from fastmcp import FastMCP

# Configuration
from app.config import Config

# Common registration logic (eliminates code duplication)
from app.common import register_all


# Create FastMCP server WITHOUT auth
mcp = FastMCP(
    name=f"{Config.SERVER_NAME} (No Auth)",
)

# Register all tools, resources, and prompts
# (eliminates ~140 lines of duplication between main.py and main_noauth.py)
register_all(mcp)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================


def run_server():
    """
    Run the MCP server without authentication

    Usage:
        # STDIO mode (default)
        python -m app.main_noauth

        # HTTP mode (local testing)
        python -m app.main_noauth --http
    """
    if "--http" in sys.argv:
        # HTTP mode for local testing
        print("🚀 Starting MCP server in HTTP mode (NO AUTH)")
        print(f"📍 Base URL: {Config.BASE_URL}")
        print(f"📡 MCP endpoint: {Config.BASE_URL}/mcp/")
        print("⚠️  Authentication: DISABLED (testing only)")
        print()

        # Extract host and port from BASE_URL
        parsed = urlparse(Config.BASE_URL)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8000

        mcp.run(transport="http", host=host, port=port)
    else:
        # STDIO mode (default)
        mcp.run()


if __name__ == "__main__":
    run_server()
