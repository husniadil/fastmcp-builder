# FastMCP Overview

## What is FastMCP?

**FastMCP** is the official high-level Python framework for building Model Context Protocol (MCP) servers. It's built on top of the MCP Python SDK and provides a simpler, more Pythonic API with significantly less boilerplate code.

## FastMCP vs MCP Python SDK

| Feature               | FastMCP                                       | MCP Python SDK                              |
| --------------------- | --------------------------------------------- | ------------------------------------------- |
| **Setup Complexity**  | Single line: `mcp = FastMCP("name")`          | Complex server initialization with handlers |
| **Tool Registration** | Decorator-based: `@mcp.tool()`                | Manual registration with schemas            |
| **Schema Generation** | Automatic from function signatures            | Manual Pydantic model definitions           |
| **Input Validation**  | Automatic with type hints                     | Manual validation code                      |
| **Code Reduction**    | ~70% less code                                | More verbose                                |
| **Learning Curve**    | Easy - familiar Python patterns               | Steeper - protocol knowledge needed         |
| **Best For**          | Rapid development, prototypes, most use cases | Low-level control, custom protocols         |

## When to Use FastMCP

**✅ Use FastMCP when:**

- Building MCP servers quickly
- You want automatic schema generation
- OAuth authentication is needed (built-in GoogleProvider)
- You prefer decorator-based APIs
- Testing with in-memory client (FastMCP Client)
- Multiple transport modes needed (stdio, HTTP, SSE)
- Context features needed (logging, progress, elicitation)

**❌ Consider MCP SDK when:**

- You need very low-level protocol control
- Custom transport implementations
- Performance is absolutely critical (minimal overhead)
- You're building SDK tooling itself

**💡 Recommendation:** Use FastMCP for 95% of use cases. It's the official recommended approach.

## Key Features

### 1. Automatic Schema Generation

FastMCP automatically generates JSON schemas from Python type hints:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def search_users(query: str, limit: int = 20) -> dict:
    """Search for users matching the query"""
    # FastMCP automatically generates:
    # - inputSchema with query (required) and limit (optional, default 20)
    # - description from docstring
    # - parameter types from type hints
    return {"users": [...]}
```

### 2. Decorator-Based Registration

Simple, Pythonic decorator pattern:

```python
# Tools
@mcp.tool()
def my_tool(param: str) -> str:
    return f"Processed: {param}"

# Resources
@mcp.resource("custom://path/{id}")
def my_resource(id: str) -> str:
    return f"Resource {id}"

# Prompts
@mcp.prompt()
def my_prompt(topic: str) -> str:
    return f"Explain {topic} in detail..."
```

### 3. Context Injection

Optional `Context` parameter provides powerful features:

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("my-server")

@mcp.tool()
async def advanced_tool(query: str, ctx: Context) -> str:
    # Logging
    await ctx.info("Processing query...")
    await ctx.debug(f"Query: {query}")

    # Progress reporting
    await ctx.report_progress(0.5, "Halfway done...")

    # Request user input
    api_key = await ctx.elicit(prompt="Enter API key:", input_type="password")

    # Access server config
    server_name = ctx.fastmcp.name

    return "Result"
```

### 4. Multiple Transport Support

Run the same server in different modes:

```python
mcp = FastMCP("my-server")

# STDIO mode (for Claude Desktop local)
mcp.run()

# HTTP mode (for remote access)
mcp.run(transport="http", host="0.0.0.0", port=8000)

# SSE mode (for Server-Sent Events)
mcp.run(transport="sse", port=8000)
```

### 5. Built-in OAuth Support

Google OAuth is built-in:

```python
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

auth = GoogleProvider(
    client_id="your-client-id",
    client_secret="your-secret",
    base_url="https://your-server.com",
    required_scopes=["openid", "email", "profile"],
)

mcp = FastMCP(name="my-server", auth=auth)
```

### 6. FastMCP Client for Testing

Test your server with in-memory client (no network, deterministic):

```python
from fastmcp import Client
from my_server import mcp

async with Client(mcp) as client:
    # Test tools
    result = await client.call_tool("search_users", {"query": "john"})
    assert result.data["status"] == "success"

    # Test resources
    content = await client.read_resource("docs://readme")
    assert "Welcome" in content

    # Test prompts
    prompt = await client.get_prompt("explain_concept", {"concept": "OAuth"})
    assert "OAuth" in prompt.messages[0].content.text
```

## Architecture

FastMCP sits on top of the MCP Python SDK:

```
Your Application Code
        ↓
FastMCP Framework (High-level API)
        ↓
MCP Python SDK (Low-level protocol)
        ↓
Transport Layer (stdio/HTTP/SSE)
```

## Getting Started

### Installation

```bash
# Install FastMCP
pip install fastmcp
# or with uv
uv add fastmcp
```

### Minimal Example

```python
from fastmcp import FastMCP

mcp = FastMCP("my-first-server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

That's it! You have a working MCP server.

## Next Steps

- See [project_structure.md](./project_structure.md) for organizing larger projects
- See [tool_patterns.md](./tool_patterns.md) for tool implementation patterns
- See [oauth_integration.md](./oauth_integration.md) for authentication
- See [testing_guide.md](./testing_guide.md) for testing strategies

## Resources

- **FastMCP Documentation**: https://gofastmcp.com/
- **FastMCP GitHub**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io/
