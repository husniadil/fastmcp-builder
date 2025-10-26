"""
Counter Tool - State Management

Demonstrates persistent state management using module-level storage.

⚠️ IMPORTANT LIMITATIONS:
- Counter stored in module-level variable (not truly persistent)
- Resets to 0 on server restart
- Does NOT work with multi-process deployments (e.g., gunicorn with multiple workers)
- Each process maintains its own separate counter value

For production use, replace with:
- Database (PostgreSQL, MySQL)
- Redis or other distributed cache
- Any shared storage solution
"""

from fastmcp import Context

# Module-level counter for demonstration
# In production, use database, Redis, or file storage
_global_counter = 0


async def counter(action: str = "get", ctx: Context | None = None) -> dict:
    """
    Stateful counter with persistent state

    Args:
        action: Action ("get", "increment", "decrement", "reset")
        ctx: FastMCP context (auto-injected)

    Returns:
        dict: Counter state and action result
    """
    global _global_counter

    try:
        if ctx:
            await ctx.info(f"📊 Counter action: {action}")

        # Perform action on global counter
        if action == "increment":
            _global_counter += 1
            if ctx:
                await ctx.info(f"➕ Incremented counter to {_global_counter}")

        elif action == "decrement":
            _global_counter -= 1
            if ctx:
                await ctx.info(f"➖ Decremented counter to {_global_counter}")

        elif action == "reset":
            _global_counter = 0
            if ctx:
                await ctx.warning("🔄 Counter reset to 0")

        elif action == "get":
            if ctx:
                await ctx.debug(f"👁️  Retrieved counter value: {_global_counter}")

        else:
            if ctx:
                await ctx.warning(f"⚠️  Unknown action: {action}")
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "valid_actions": ["get", "increment", "decrement", "reset"],
            }

        return {
            "status": "success",
            "count": _global_counter,
            "action": action,
            "features_demonstrated": ["persistent_state", "module_level_storage"],
            "note": "Using module-level variable since ctx.get_state/set_state are request-scoped",
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Counter operation failed: {str(e)}")
        return {"status": "error", "error": str(e), "action": action}
