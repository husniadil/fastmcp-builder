"""
Configuration management for MCP Auth Demo

Loads environment variables and provides centralized configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""

    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Server configuration
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

    # OAuth scopes required
    REQUIRED_SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    # OAuth redirect path
    REDIRECT_PATH = "/auth/callback"

    # Server metadata
    SERVER_NAME = "MCP Auth Demo"
    SERVER_VERSION = "2.0.0"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.GOOGLE_CLIENT_ID or not cls.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Missing required environment variables. "
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file"
            )


# Validate configuration on import
Config.validate()
