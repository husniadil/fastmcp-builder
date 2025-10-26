#!/usr/bin/env python3
"""
Minimal FastMCP Server Example

The absolute simplest FastMCP server possible.
Perfect for learning or quick prototypes.

Run:
    python minimal_server.py
"""

from fastmcp import FastMCP

# Create server
mcp = FastMCP("minimal-server")


# Add a single tool
@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"


# Run server
if __name__ == "__main__":
    mcp.run()
