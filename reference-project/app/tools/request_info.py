"""
Request Info Tool - Request Metadata

Access MCP request metadata including request ID, client ID, and session info.
"""

from fastmcp import Context


async def get_request_info(ctx: Context | None = None) -> dict:
    """
    Get current request metadata

    Args:
        ctx: FastMCP context (auto-injected)

    Returns:
        dict: Request ID, client ID, session ID, and server info
    """
    if not ctx:
        return {
            "error": "Context not available",
            "note": "This tool requires MCP context to access request metadata",
        }

    try:
        # Get request metadata
        result = {
            "status": "success",
            "request": {
                "request_id": ctx.request_id if hasattr(ctx, "request_id") else None,
                "client_id": ctx.client_id if hasattr(ctx, "client_id") else None,
                "session_id": (
                    ctx.session_id if hasattr(ctx, "session_id") else "N/A (STDIO mode)"
                ),
            },
            "server": {
                "name": ctx.fastmcp.name if hasattr(ctx, "fastmcp") else "Unknown",
                "transport": "HTTP"
                if hasattr(ctx, "session_id") and ctx.session_id
                else "STDIO",
            },
            "features_demonstrated": ["request_metadata", "context_access"],
        }

        # Log the access
        await ctx.info("📋 Request metadata accessed")
        await ctx.debug(f"Request ID: {result['request']['request_id']}")

        return result

    except Exception as e:
        await ctx.error(f"❌ Failed to get request info: {str(e)}")
        return {"status": "error", "error": str(e)}
