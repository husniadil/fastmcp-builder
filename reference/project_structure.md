# FastMCP Project Structure

## Recommended Structure

For production FastMCP servers, use this proven structure:

```
my-mcp-server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Server with OAuth (production)
│   ├── main_noauth.py         # Server without OAuth (local testing)
│   ├── common.py              # Shared registration logic (DRY principle)
│   ├── config.py              # Configuration management
│   │
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py
│   │   ├── ping.py           # Health check
│   │   ├── search.py         # Business logic tools
│   │   └── ...
│   │
│   ├── resources/            # Resource implementations
│   │   ├── __init__.py
│   │   ├── welcome.py        # Dynamic resources
│   │   ├── static.py         # Static resources
│   │   └── ...
│   │
│   └── prompts/              # Prompt implementations
│       ├── __init__.py
│       ├── explain.py
│       └── ...
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_tools.py         # Tool tests
│   ├── test_resources.py     # Resource tests
│   ├── test_prompts.py       # Prompt tests
│   └── test_client.py        # End-to-end tests with Client
│
├── pyproject.toml            # Project dependencies
├── .env.example              # Environment template
├── .env                      # Actual environment (gitignored)
└── README.md                 # Documentation
```

## Why This Structure?

### 1. Separation of Concerns

Each component type has its own directory:

- **tools/**: Business logic operations
- **resources/**: Data access endpoints
- **prompts/**: Reusable message templates

This makes it easy to find and maintain code.

### 2. DRY Principle with common.py

The `common.py` pattern eliminates code duplication:

**Without common.py** (❌ Bad):

```python
# main.py
from app.tools.ping import ping
from app.tools.search import search
# ...20 more imports

mcp = FastMCP("my-server", auth=auth)
mcp.tool()(ping)
mcp.tool()(search)
# ...20 more registrations

# main_noauth.py - DUPLICATED CODE!
from app.tools.ping import ping
from app.tools.search import search
# ...20 more imports

mcp = FastMCP("my-server")  # No auth
mcp.tool()(ping)
mcp.tool()(search)
# ...20 more registrations
```

**With common.py** (✅ Good):

```python
# common.py
def register_all(mcp: FastMCP) -> None:
    """Register all components - defined once, used everywhere"""
    from app.tools.ping import ping
    from app.tools.search import search

    mcp.tool()(ping)
    mcp.tool()(search)
    # ...all registrations in one place

# main.py
from app.common import register_all
mcp = FastMCP("my-server", auth=auth)
register_all(mcp)

# main_noauth.py
from app.common import register_all
mcp = FastMCP("my-server")
register_all(mcp)
```

### 3. Dual-Mode Pattern

Having both `main.py` (with OAuth) and `main_noauth.py` (without OAuth):

**Benefits:**

- ✅ Local development without OAuth setup
- ✅ Faster testing (no network calls)
- ✅ CI/CD friendly (no credentials needed)
- ✅ Easy debugging in STDIO mode

**When to use each:**

- `main_noauth.py`: Local development, testing, STDIO mode
- `main.py`: Production deployment, remote access, OAuth required

## File Details

### app/main.py (Production Server with OAuth)

```python
"""Production server with Google OAuth"""

import argparse
from urllib.parse import urlparse
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

from app.config import Config
from app.common import register_all

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--http", action="store_true")
parser.add_argument("--base-url", type=str, default=Config.BASE_URL)
args, unknown = parser.parse_known_args()

# Setup OAuth
auth = GoogleProvider(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    base_url=args.base_url,
    required_scopes=Config.REQUIRED_SCOPES,
    redirect_path=Config.REDIRECT_PATH,
)

# Create server with auth
mcp = FastMCP(name=Config.SERVER_NAME, auth=auth)

# Register all components
register_all(mcp)

def run_server():
    if args.http:
        parsed = urlparse(args.base_url)
        port = parsed.port or 8000
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()

if __name__ == "__main__":
    run_server()
```

### app/main_noauth.py (Local Testing Without OAuth)

```python
"""Local server without OAuth for testing"""

import sys
from urllib.parse import urlparse
from fastmcp import FastMCP

from app.config import Config
from app.common import register_all

# Create server WITHOUT auth
mcp = FastMCP(name=f"{Config.SERVER_NAME} (No Auth)")

# Register all components (same function as main.py)
register_all(mcp)

def run_server():
    if "--http" in sys.argv:
        parsed = urlparse(Config.BASE_URL)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8000
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()

if __name__ == "__main__":
    run_server()
```

### app/common.py (Shared Registration)

```python
"""Shared registration logic for both main.py and main_noauth.py"""

from fastmcp import FastMCP

# Tool imports
from app.tools.ping import ping
from app.tools.search import search_users

# Resource imports
from app.resources.welcome import get_welcome_message
from app.resources.static import get_static_resources

# Prompt imports
from app.prompts.explain import explain_concept


def register_all(mcp: FastMCP) -> None:
    """
    Register all tools, resources, and prompts

    This function eliminates duplication between main.py and main_noauth.py.
    Any new component should be registered here once.
    """

    # ============================================================================
    # TOOLS
    # ============================================================================
    mcp.tool()(ping)
    mcp.tool()(search_users)

    # ============================================================================
    # RESOURCES
    # ============================================================================
    mcp.resource("greeting://welcome")(get_welcome_message)

    # Static resources
    static_resources = get_static_resources()

    @mcp.resource("text://status")
    def get_status():
        return static_resources[0].text

    # ============================================================================
    # PROMPTS
    # ============================================================================
    mcp.prompt()(explain_concept)
```

### app/config.py (Configuration Management)

```python
"""Configuration management with environment variables"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Server configuration
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

    # OAuth scopes
    REQUIRED_SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    # OAuth redirect
    REDIRECT_PATH = "/auth/callback"

    # Server metadata
    SERVER_NAME = "My MCP Server"
    SERVER_VERSION = "1.0.0"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.GOOGLE_CLIENT_ID or not cls.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Missing GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET. "
                "Please set them in .env file"
            )


# Validate on import
Config.validate()
```

> **Important:** The Config class calls `Config.validate()` automatically on import (see the last two lines above). This validates that required environment variables are set.
>
> **Before importing `app.config`**, ensure you have a `.env` file with `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, otherwise you'll get a `ValueError`.
>
> **For testing without OAuth:**
>
> - Use `main_noauth.py` which doesn't import the full config validation
> - Or use the `mock_env` fixture provided in `tests/conftest.py`
> - Or set the environment variables before running tests

### pyproject.toml (Dependencies)

```toml
[project]
name = "my-mcp-server"
version = "1.0.0"
description = "My FastMCP server"
requires-python = ">=3.11"
dependencies = [
    "fastmcp==2.13.0.1",
    "python-dotenv==1.2.1",
]

[project.optional-dependencies]
test = [
    "pytest==8.4.2",
    "pytest-asyncio==1.2.0",
    "pytest-mock==3.15.1",
    "httpx==0.28.1",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--strict-markers", "--tb=short"]
```

## Development Workflow

### 1. Local Development

```bash
# Run without OAuth (fast, easy)
uv run python -m app.main_noauth

# Or with HTTP for testing
uv run python -m app.main_noauth --http
```

### 2. Production Deployment

```bash
# With OAuth and ngrok
ngrok http 8000

# In another terminal
uv run python -m app.main --http --base-url https://your-ngrok-url.ngrok-free.app
```

### 3. Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_client.py -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=html
```

## Adding New Components

### Adding a New Tool

1. Create `app/tools/my_tool.py`:

```python
async def my_tool(param: str) -> dict:
    """My tool description"""
    return {"result": f"Processed: {param}"}
```

2. Register in `app/common.py`:

```python
from app.tools.my_tool import my_tool

def register_all(mcp: FastMCP) -> None:
    mcp.tool()(my_tool)  # Add this line
    # ...other registrations
```

That's it! Now it works in both `main.py` and `main_noauth.py`.

### Adding a New Resource

1. Create `app/resources/my_resource.py`:

```python
def get_my_data() -> str:
    """My resource"""
    return "My data content"
```

2. Register in `app/common.py`:

```python
from app.resources.my_resource import get_my_data

def register_all(mcp: FastMCP) -> None:
    mcp.resource("custom://mydata")(get_my_data)  # Add this line
    # ...other registrations
```

## Best Practices

1. **✅ Use common.py pattern** - Eliminate duplication
2. **✅ Provide both auth and no-auth versions** - Better DX
3. **✅ Separate tools/resources/prompts** - Clear organization
4. **✅ Use Config class** - Centralized configuration
5. **✅ Add comprehensive tests** - Quality assurance
6. **✅ Document in README** - Help others (and future you)

## Example: mcp-auth-demo

The [mcp-auth-demo](https://github.com/yourusername/mcp-auth-demo) project follows this exact structure with:

- 6 production tools
- 7 resource instances (4 types)
- 1 universal prompt
- 145 passing tests
- OAuth integration
- Comprehensive documentation

It's a complete reference implementation of these patterns.
