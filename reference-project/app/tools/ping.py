"""
Ping Tool - Health Check

Simple health check endpoint returning server status and response time.
"""

from datetime import datetime, timezone
import time
from app.config import Config


def ping() -> dict:
    """
    Check server connectivity and response time

    Returns:
        dict: Status, timestamp, response time, and server metadata
    """
    try:
        start_time = time.time()

        response = {
            "status": "ok",
            "message": "pong",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "server": {
                "name": Config.SERVER_NAME,
                "version": Config.SERVER_VERSION,
                "base_url": Config.BASE_URL,
            },
        }

        return response

    except Exception as e:
        # Defensive error handling for consistency with other tools
        return {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
        }
