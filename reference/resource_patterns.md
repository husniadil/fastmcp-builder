# FastMCP Resource Patterns

Resources in FastMCP provide read-only access to data through URI-based endpoints. They're perfect for exposing static or semi-static content that doesn't require complex parameters.

## Resource vs Tool

**Use Resources when:**

- ✅ Read-only data access
- ✅ Simple parameters (URI-based)
- ✅ Static or semi-static content
- ✅ Documentation, config, status

**Use Tools when:**

- ✅ Complex operations
- ✅ Multiple parameters with validation
- ✅ Write operations
- ✅ Business logic

## Resource Types in FastMCP

FastMCP supports 4 types of resources:

1. **Static Resources** (Class-based) - Fixed content
2. **Dynamic Resources** (Function-based) - Generated content
3. **Template Resources** - With path parameters
4. **Wildcard Resources** - Match multiple segments

## 1. Static Resources (Class-Based)

**Pattern:** Fixed, pre-defined content using TextResource or FileResource

### TextResource Example

```python
from fastmcp.resources import TextResource

# Create static text resource
status_resource = TextResource(
    uri="text://status",
    text="🟢 Server is operational\n\nAll systems running normally.",
    name="Server Status",
    description="Current server operational status",
    mime_type="text/plain",
)

# Features list as markdown
features_resource = TextResource(
    uri="text://features",
    text="""# Server Features

✅ OAuth Authentication
✅ Production Tools
✅ Static & Dynamic Resources
✅ Universal Prompts
✅ Logging & Progress Tracking

See README.md for complete documentation.
""",
    name="Feature List",
    description="List of implemented features",
    mime_type="text/markdown",
)
```

### FileResource Example

```python
from fastmcp.resources import FileResource
from pathlib import Path

# Expose README file
readme_resource = FileResource(
    uri="file://readme",
    path=Path(__file__).parent.parent / "README.md",
    name="Project README",
    description="Complete project documentation",
    mime_type="text/markdown",
)

# Conditional file resource (only if file exists)
test_results_path = Path(__file__).parent.parent / "TEST_RESULTS.md"
if test_results_path.exists():
    test_results_resource = FileResource(
        uri="file://test-results",
        path=test_results_path,
        name="Test Results",
        description="Complete test results and compatibility matrix",
        mime_type="text/markdown",
    )
else:
    test_results_resource = None
```

### Registration (Class-Based Resources)

Class-based resources need to be converted to functions for registration:

```python
# In app/resources/static.py
def get_static_resources():
    """Get all static resources"""
    resources = [
        status_resource,
        features_resource,
        readme_resource,
    ]

    if test_results_resource:
        resources.append(test_results_resource)

    return resources


# In app/common.py
from app.resources.static import get_static_resources

def register_all(mcp: FastMCP) -> None:
    # Get static resources
    static_resources = get_static_resources()

    # Register each with wrapper function
    @mcp.resource("text://status")
    def get_status():
        return static_resources[0].text

    @mcp.resource("text://features")
    def get_features():
        return static_resources[1].text

    @mcp.resource("file://readme")
    def get_readme():
        return static_resources[2].path.read_text()

    # Conditional resource
    if len(static_resources) > 3:
        @mcp.resource("file://test-results")
        def get_test_results():
            return static_resources[3].path.read_text()
```

**Use When:**

- Fixed content (status messages, feature lists)
- Exposing local files (README, docs, configs)
- No computation needed

---

## 2. Dynamic Resources (Function-Based)

**Pattern:** Generated content using functions

### Simple Dynamic Resource

```python
from app.config import Config


def get_welcome_message() -> str:
    """
    Welcome message resource

    URI: greeting://welcome

    Returns:
        Welcome message with server info
    """
    return f"""Welcome to {Config.SERVER_NAME}! 🎉

This is a FastMCP server demonstrating:
✅ Google OAuth 2.0 authentication
✅ Basic and advanced tools
✅ Static and template resources
✅ Reusable prompts
✅ Advanced FastMCP features

Server Version: {Config.SERVER_VERSION}
Base URL: {Config.BASE_URL}

Get started by exploring available tools and resources!
"""
```

**Registration:**

```python
mcp.resource("greeting://welcome")(get_welcome_message)
```

**Use When:**

- Content generated at request time
- Includes dynamic data (timestamps, config)
- Simple computation

---

## 3. Template Resources (Path Parameters)

**Pattern:** Resources with path parameters in the URI

### Template with Single Parameter

```python
import json
from fastmcp import Context


async def get_user_info(
    user_id: str, format: str = "json", ctx: Context | None = None
) -> str:
    """
    Get user information in different formats

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

    # Optional: Log resource access
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
```

**Registration:**

```python
mcp.resource("userinfo://{user_id}")(get_user_info)
```

**Access:**

```
userinfo://123           # JSON (default)
userinfo://123?format=xml  # XML
userinfo://123?format=text # Text
```

**Use When:**

- Need parameter in URI path
- Multiple output formats
- Database/API lookups by ID

---

## 4. Wildcard Resources (Multi-Segment Paths)

**Pattern:** Resources matching multiple URI segments with `{path*}`

### Wildcard Documentation Resource

```python
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

    Examples:
        docs://getting-started          → "getting-started"
        docs://api/tools/advanced       → "api/tools/advanced"

    URI Template: docs://{path*}
    """
    if ctx:
        await ctx.info(f"📖 Fetching documentation: {path}")

    # Map of available documentation
    docs_map = {
        "getting-started": """# Getting Started

Welcome! This guide will help you get started.

## Quick Start:
1. Clone the repository
2. Configure environment
3. Run the server
4. Connect from Claude Desktop

See README.md for complete documentation.
""",
        "api/tools": """# API - Tools

## Available Tools:

### Basic Tools:
- **ping** - Health check
- **get_request_info** - Request metadata

### Text Processing:
- **analyze_text** - Text statistics
- **process_text** - Advanced processor

## Usage:
Each tool is callable via MCP protocol.
""",
        "api/resources": """# API - Resources

## Available Resources:

### Dynamic Resources:
- **greeting://welcome** - Welcome message
- **userinfo://{user_id}** - User information

### Static Resources:
- **text://status** - Server status
- **file://readme** - Project README

### Wildcard Resources:
- **docs://{path*}** - Documentation (you're reading it!)

## Usage:
Resources are read-only, accessed via URI scheme.
""",
        "guides/oauth": """# OAuth Setup Guide

## Google OAuth Configuration:

1. Create OAuth Client in Google Cloud Console
2. Configure Redirect URI
3. Set environment variables
4. Start server with OAuth
5. Connect Claude Desktop

See oauth_integration.md for complete guide.
""",
    }

    # Check if path exists
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

**Note:** This resource uses wildcard parameter {{path*}} which matches multiple URI segments.
"""
```

**Registration:**

```python
mcp.resource("docs://{path*}")(get_documentation)
```

**Access:**

```
docs://getting-started
docs://api/tools
docs://api/resources
docs://guides/oauth
```

**Use When:**

- Hierarchical content (docs, file trees)
- Need to match multiple path segments
- Dynamic routing

---

## Complete Registration Example

```python
# In app/common.py

from fastmcp import FastMCP

# Resource imports
from app.resources.welcome import get_welcome_message
from app.resources.userinfo import get_user_info
from app.resources.static import get_static_resources
from app.resources.docs import get_documentation


def register_all(mcp: FastMCP) -> None:
    """Register all resources"""

    # ============================================================================
    # DYNAMIC RESOURCES (Function-Based)
    # ============================================================================

    mcp.resource("greeting://welcome")(get_welcome_message)
    mcp.resource("userinfo://{user_id}")(get_user_info)

    # ============================================================================
    # WILDCARD RESOURCES
    # ============================================================================

    mcp.resource("docs://{path*}")(get_documentation)

    # ============================================================================
    # STATIC RESOURCES (Class-Based, wrapped in functions)
    # ============================================================================

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

    # Conditional resource
    if len(static_resources) > 3:
        @mcp.resource("file://test-results")
        def get_test_results():
            return static_resources[3].path.read_text()
```

## Best Practices

### 1. URI Schemes

Use descriptive URI schemes:

```python
# ✅ Good: Clear schemes
mcp.resource("docs://readme")
mcp.resource("config://server")
mcp.resource("user://{id}")

# ❌ Bad: Generic schemes
mcp.resource("resource://1")
mcp.resource("data://thing")
```

### 2. Error Handling

Handle missing resources gracefully:

```python
async def get_resource(id: str, ctx: Context | None = None) -> str:
    data = fetch_from_db(id)

    if not data:
        if ctx:
            await ctx.warning(f"Resource not found: {id}")
        return f"Resource {id} not found"

    return format_data(data)
```

### 3. MIME Types

Set appropriate MIME types for static resources:

```python
TextResource(
    uri="text://status",
    text="...",
    mime_type="text/plain"  # or "text/markdown", "application/json"
)
```

### 4. Documentation

Document URI patterns clearly:

```python
async def get_user(user_id: str) -> str:
    """
    Get user details

    URI Pattern: user://{user_id}

    Examples:
        user://123  → User details for ID 123
        user://abc  → User details for ID abc
    """
    pass
```

## Testing Resources

```python
from fastmcp import Client
from app.main_noauth import mcp

async with Client(mcp) as client:
    # List all resources
    resources = await client.list_resources()
    assert len(resources) > 0

    # Read specific resource
    content = await client.read_resource("greeting://welcome")
    assert "Welcome" in content

    # Read template resource
    user_json = await client.read_resource("userinfo://123")
    assert "user123@example.com" in user_json

    # Read wildcard resource
    docs = await client.read_resource("docs://getting-started")
    assert "Getting Started" in docs
```

## Summary

| Type              | Pattern      | Use Case            | Example URI          |
| ----------------- | ------------ | ------------------- | -------------------- |
| **Static (Text)** | TextResource | Fixed text content  | `text://status`      |
| **Static (File)** | FileResource | Expose local files  | `file://readme`      |
| **Dynamic**       | Function     | Generated content   | `greeting://welcome` |
| **Template**      | `{param}`    | Path parameters     | `user://{id}`        |
| **Wildcard**      | `{path*}`    | Multi-segment paths | `docs://{path*}`     |

Choose the type that best fits your data access pattern!
