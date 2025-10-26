"""
Docs Resource - Demonstrates Wildcard Parameters

Shows how to use {path*} wildcard parameter to match multiple URI segments.

Example URIs:
- docs://getting-started          → matches with path="getting-started"
- docs://api/tools                → matches with path="api/tools"
- docs://guides/oauth/setup       → matches with path="guides/oauth/setup"

The wildcard {path*} captures everything after docs:// as a single parameter.
"""

from fastmcp import Context


async def get_documentation(path: str, ctx: Context | None = None) -> str:
    """
    Get documentation content using wildcard path matching

    Args:
        path: Path segments captured by {path*} wildcard
              Can be single segment or multiple segments separated by /
        ctx: FastMCP context (optional)

    Returns:
        Documentation content

    Example:
        docs://getting-started          → "getting-started"
        docs://api/tools/advanced       → "api/tools/advanced"

    URI Template: docs://{path*}
    """
    if ctx:
        await ctx.info(f"📖 Fetching documentation: {path}")

    # Map of available documentation
    docs_map = {
        "getting-started": """# Getting Started with MCP Auth Demo

Welcome! This is a minimalist MCP server demonstrating all core features.

## Quick Start:
1. Clone the repository
2. Configure .env with Google OAuth credentials
3. Run: `./run.sh --http --base-url https://your-ngrok-url.ngrok-free.app`
4. Connect from Claude Desktop

## Features:
- OAuth authentication
- Tools (basic, advanced, debug)
- Resources (dynamic, static, template)
- Prompts
- State management

See README.md for complete documentation.
""",
        "api/tools": """# API - Tools

## Available Tools:

### Basic Tools:
- **ping** - Health check
- **get_request_info** - Request metadata
- **counter** - State management demo

### Text Processing:
- **analyze_text** - Text statistics
- **process_text** - Production text processor (RECOMMENDED)
- **process_content** - Full demo (MCP Inspector only)

### Debug Tools:
- **test_context** - Test Context operations
- **test_sampling** - Test LLM sampling
- **test_elicitation** - Test elicitation

## Usage:
Each tool is callable via MCP protocol with type-safe parameters.
""",
        "api/resources": """# API - Resources

## Available Resources:

### Dynamic Resources (Function-Based):
- **greeting://welcome** - Welcome message
- **userinfo://{user_id}** - User information with format parameter

### Static Resources (Class-Based):
- **text://status** - Server status
- **text://features** - Feature list
- **file://readme** - Project README
- **file://test-results** - Test results

### Wildcard Resources:
- **docs://{path*}** - Documentation (you're reading it!)

## Usage:
Resources are read-only and accessed via URI scheme.
""",
        "guides/oauth": """# OAuth Setup Guide

## Google OAuth Configuration:

1. **Create OAuth Client:**
   - Go to Google Cloud Console
   - Create OAuth 2.0 Client ID
   - Type: Web application

2. **Configure Redirect URI:**
   - Add: https://your-ngrok-url.ngrok-free.app/auth/callback
   - Note: Only ONE redirect URI needed (server's callback)

3. **Start Server:**
   ```bash
   uv run python -m app.main --http --base-url https://your-ngrok-url.ngrok-free.app
   ```

4. **Connect Claude Desktop:**
   - Open Claude Desktop
   - Go to Settings > Connectors
   - Click "Add custom connector"
   - Enter URL: https://your-ngrok-url.ngrok-free.app
   - Claude handles OAuth automatically

   Note: Requires Claude Pro/Max/Team/Enterprise plan.
   HTTP servers cannot use claude_desktop_config.json.

## Troubleshooting:
See README.md for complete setup instructions.
""",
        "troubleshooting": """# Troubleshooting

## Common Issues:

### 1. Tools Hang
**Symptom:** Tool never returns
**Cause:** Uses ctx.list_roots() or ctx.sample()
**Solution:** Use stable tools (ping, analyze_text, process_text)

### 2. OAuth Redirect Mismatch
**Symptom:** Error 400: redirect_uri_mismatch
**Cause:** Redirect URI not in Google Console
**Solution:** Add https://your-ngrok-url.ngrok-free.app/auth/callback

### 3. State Doesn't Persist
**Symptom:** Counter resets every call
**Note:** This is expected! ctx.get_state/set_state are request-scoped.
**Current:** Using module-level variable for demonstration.

### 4. Resources Not Found
**Symptom:** "Resource not found"
**Solution:** Check server logs for registration errors

See TEST_RESULTS.md for complete compatibility matrix.
""",
    }

    # Check if path exists in docs map
    if path in docs_map:
        if ctx:
            await ctx.debug(f"✅ Found documentation for: {path}")
        return docs_map[path]

    # If not found, return list of available docs
    if ctx:
        await ctx.warning(f"⚠️  Documentation not found: {path}")

    available_docs = "\n".join(f"- docs://{p}" for p in docs_map.keys())

    return f"""# Documentation Not Found

The path '{path}' does not exist.

## Available Documentation:

{available_docs}

## Examples:
- docs://getting-started
- docs://api/tools
- docs://guides/oauth
- docs://troubleshooting

**Note:** This resource uses wildcard parameter {{path*}} which matches multiple URI segments.
"""
