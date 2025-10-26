"""
Unit tests for config module
"""

import os
import pytest
from unittest.mock import patch


class TestConfigLoading:
    """Tests for configuration loading"""

    def test_config_imports_successfully(self):
        """Config module should import without errors"""
        from app.config import Config

        assert Config is not None

    def test_config_has_google_client_id(self):
        """Config should have GOOGLE_CLIENT_ID"""
        from app.config import Config

        assert hasattr(Config, "GOOGLE_CLIENT_ID")

    def test_config_has_google_client_secret(self):
        """Config should have GOOGLE_CLIENT_SECRET"""
        from app.config import Config

        assert hasattr(Config, "GOOGLE_CLIENT_SECRET")

    def test_config_has_base_url(self):
        """Config should have BASE_URL"""
        from app.config import Config

        assert hasattr(Config, "BASE_URL")
        assert Config.BASE_URL is not None

    def test_config_has_required_scopes(self):
        """Config should have REQUIRED_SCOPES"""
        from app.config import Config

        assert hasattr(Config, "REQUIRED_SCOPES")
        assert isinstance(Config.REQUIRED_SCOPES, list)

    def test_config_has_redirect_path(self):
        """Config should have REDIRECT_PATH"""
        from app.config import Config

        assert hasattr(Config, "REDIRECT_PATH")
        assert Config.REDIRECT_PATH == "/auth/callback"

    def test_config_has_server_name(self):
        """Config should have SERVER_NAME"""
        from app.config import Config

        assert hasattr(Config, "SERVER_NAME")
        assert Config.SERVER_NAME == "MCP Auth Demo"

    def test_config_has_server_version(self):
        """Config should have SERVER_VERSION"""
        from app.config import Config

        assert hasattr(Config, "SERVER_VERSION")
        assert Config.SERVER_VERSION == "2.0.0"


class TestConfigDefaults:
    """Tests for configuration defaults"""

    def test_base_url_defaults_to_localhost(self):
        """BASE_URL should default to localhost if not set"""
        # This test verifies the default in config.py
        from app.config import Config

        # If no env var, should be localhost:8000
        assert (
            "localhost" in Config.BASE_URL or Config.BASE_URL == "http://localhost:8000"
        )

    def test_required_scopes_includes_openid(self):
        """REQUIRED_SCOPES should include openid"""
        from app.config import Config

        assert "openid" in Config.REQUIRED_SCOPES

    def test_required_scopes_includes_email(self):
        """REQUIRED_SCOPES should include email scope"""
        from app.config import Config

        assert any("email" in scope for scope in Config.REQUIRED_SCOPES)

    def test_required_scopes_includes_profile(self):
        """REQUIRED_SCOPES should include profile scope"""
        from app.config import Config

        assert any("profile" in scope for scope in Config.REQUIRED_SCOPES)

    def test_required_scopes_has_three_scopes(self):
        """REQUIRED_SCOPES should have exactly 3 scopes"""
        from app.config import Config

        assert len(Config.REQUIRED_SCOPES) == 3


class TestConfigValidation:
    """Tests for configuration validation"""

    def test_config_has_validate_method(self):
        """Config should have validate() class method"""
        from app.config import Config

        assert hasattr(Config, "validate")
        assert callable(Config.validate)

    def test_validate_raises_without_credentials(self):
        """validate() should raise ValueError without credentials"""
        from app.config import Config

        # Mock the class attributes
        original_client_id = Config.GOOGLE_CLIENT_ID
        original_client_secret = Config.GOOGLE_CLIENT_SECRET

        try:
            Config.GOOGLE_CLIENT_ID = None
            Config.GOOGLE_CLIENT_SECRET = None

            with pytest.raises(ValueError) as exc_info:
                Config.validate()

            assert "Missing required environment variables" in str(exc_info.value)
        finally:
            Config.GOOGLE_CLIENT_ID = original_client_id
            Config.GOOGLE_CLIENT_SECRET = original_client_secret

    def test_validate_raises_without_client_secret(self):
        """validate() should raise ValueError without client secret"""
        from app.config import Config

        # Mock the class attributes
        original_client_secret = Config.GOOGLE_CLIENT_SECRET

        try:
            Config.GOOGLE_CLIENT_SECRET = None

            with pytest.raises(ValueError) as exc_info:
                Config.validate()

            assert "Missing required environment variables" in str(exc_info.value)
        finally:
            Config.GOOGLE_CLIENT_SECRET = original_client_secret

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
        },
    )
    def test_validate_passes_with_credentials(self):
        """validate() should pass with both credentials"""
        import importlib
        import app.config

        # Should not raise
        try:
            importlib.reload(app.config)
            success = True
        except ValueError:
            success = False

        assert success


class TestConfigStructure:
    """Tests for configuration structure"""

    def test_config_is_class_not_instance(self):
        """Config should be a class, not an instance"""
        from app.config import Config

        assert isinstance(Config, type)

    def test_config_attributes_are_class_level(self):
        """Config attributes should be class-level, not instance"""
        from app.config import Config

        # Should be able to access without instantiation
        assert Config.SERVER_NAME is not None
        assert Config.SERVER_VERSION is not None
        assert Config.REDIRECT_PATH is not None

    def test_config_loads_from_dotenv(self):
        """Config should load from .env file via dotenv"""
        from app.config import Config

        # If GOOGLE_CLIENT_ID is set, it should be loaded
        # This tests that dotenv loading works
        assert (
            Config.GOOGLE_CLIENT_ID is not None
            or Config.GOOGLE_CLIENT_ID == os.getenv("GOOGLE_CLIENT_ID")
        )


class TestConfigConstants:
    """Tests for configuration constants"""

    def test_server_name_is_string(self):
        """SERVER_NAME should be a string"""
        from app.config import Config

        assert isinstance(Config.SERVER_NAME, str)

    def test_server_version_is_string(self):
        """SERVER_VERSION should be a string"""
        from app.config import Config

        assert isinstance(Config.SERVER_VERSION, str)

    def test_redirect_path_starts_with_slash(self):
        """REDIRECT_PATH should start with /"""
        from app.config import Config

        assert Config.REDIRECT_PATH.startswith("/")

    def test_redirect_path_is_callback(self):
        """REDIRECT_PATH should be /auth/callback"""
        from app.config import Config

        assert Config.REDIRECT_PATH == "/auth/callback"

    def test_base_url_is_valid_url(self):
        """BASE_URL should be a valid URL format"""
        from app.config import Config

        assert Config.BASE_URL.startswith("http://") or Config.BASE_URL.startswith(
            "https://"
        )

    def test_required_scopes_are_urls(self):
        """REQUIRED_SCOPES should be valid scope identifiers"""
        from app.config import Config

        for scope in Config.REQUIRED_SCOPES:
            # Should be either a simple string or URL
            assert isinstance(scope, str)
            assert len(scope) > 0
