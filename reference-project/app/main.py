"""
MCP Auth Demo - Production Server with Google OAuth

A minimalist MCP server demonstrating:
- Google OAuth 2.0 authentication
- Production-ready tools and resources
- Clean, maintainable architecture
"""

import argparse
from urllib.parse import urlparse
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

# Configuration
from app.config import Config

# Common registration logic (eliminates code duplication)
from app.common import register_all


# Parse command-line arguments
parser = argparse.ArgumentParser(description="MCP Auth Demo Server")
parser.add_argument(
    "--http", action="store_true", help="Run in HTTP mode (default: stdio)"
)
parser.add_argument(
    "--base-url",
    type=str,
    default=Config.BASE_URL,
    help="Override base URL (e.g., https://your-ngrok-url.ngrok-free.app)",
)
args, unknown = parser.parse_known_args()

# Setup Google OAuth Provider
auth = GoogleProvider(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    base_url=args.base_url,
    required_scopes=Config.REQUIRED_SCOPES,
    redirect_path=Config.REDIRECT_PATH,
)

# Create FastMCP server with authentication
mcp = FastMCP(
    name=Config.SERVER_NAME,
    auth=auth,
)

# Register all tools, resources, and prompts
# (eliminates ~140 lines of duplication between main.py and main_noauth.py)
register_all(mcp)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================


def run_server():
    """
    Run the MCP server

    Modes:
    - stdio: Default mode for Claude Desktop (local)
    - http: HTTP mode for remote access (ngrok)

    Usage:
        # STDIO mode
        python -m app.main

        # HTTP mode with ngrok
        python -m app.main --http --base-url https://your-ngrok-url.ngrok-free.app
    """
    if args.http:
        # HTTP mode for remote access
        print("🚀 Starting MCP server in HTTP mode")
        print(f"📍 Base URL: {args.base_url}")
        print(f"📡 MCP endpoint: {args.base_url}/mcp/")
        print(
            f"🔐 OAuth metadata: {args.base_url}/.well-known/oauth-authorization-server"
        )
        print()

        # Extract port from base URL (default: 8000)
        parsed = urlparse(args.base_url)
        port = parsed.port or 8000

        # Always bind to 0.0.0.0 for ngrok compatibility
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        # STDIO mode (default)
        mcp.run()


if __name__ == "__main__":
    run_server()
