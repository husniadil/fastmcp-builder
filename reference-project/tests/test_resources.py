"""
Unit tests for resources
"""

import pytest
import json
from app.resources.welcome import get_welcome_message
from app.resources.userinfo import get_user_info
from app.resources.static import get_static_resources
from app.resources.docs import get_documentation


class TestWelcomeResource:
    """Tests for static welcome resource"""

    def test_welcome_returns_string(self):
        """get_welcome_message() should return a string"""
        result = get_welcome_message()
        assert isinstance(result, str)

    def test_welcome_contains_server_name(self):
        """get_welcome_message() should contain server name"""
        result = get_welcome_message()
        assert "MCP Auth Demo" in result

    def test_welcome_contains_version(self):
        """get_welcome_message() should contain version info"""
        result = get_welcome_message()
        assert "2.0.0" in result

    def test_welcome_not_empty(self):
        """get_welcome_message() should not be empty"""
        result = get_welcome_message()
        assert len(result) > 0


class TestUserInfoResource:
    """Tests for template userinfo resource"""

    @pytest.mark.asyncio
    async def test_userinfo_returns_string(self):
        """get_user_info() should return a string"""
        result = await get_user_info("123")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_userinfo_default_format_is_json(self):
        """get_user_info() should return JSON by default"""
        result = await get_user_info("123")

        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_userinfo_json_format(self):
        """get_user_info() with format=json should return valid JSON"""
        result = await get_user_info("456", format="json")

        data = json.loads(result)
        assert data["user_id"] == "456"
        assert "name" in data
        assert "email" in data

    @pytest.mark.asyncio
    async def test_userinfo_xml_format(self):
        """get_user_info() with format=xml should return XML"""
        result = await get_user_info("789", format="xml")

        # Should contain XML markers
        assert '<?xml version="1.0"' in result
        assert "<user>" in result
        assert "</user>" in result
        assert "<id>789</id>" in result

    @pytest.mark.asyncio
    async def test_userinfo_text_format(self):
        """get_user_info() with format=text should return plain text"""
        result = await get_user_info("101", format="text")

        # Should be plain text (not JSON or XML)
        assert "ID: 101" in result
        assert "Name:" in result
        assert "Email:" in result

        # Should NOT be JSON or XML
        assert not result.startswith("{")
        assert not result.startswith("<?xml")

    @pytest.mark.asyncio
    async def test_userinfo_uses_user_id(self):
        """get_user_info() should use provided user_id"""
        result = await get_user_info("999", format="json")

        data = json.loads(result)
        assert data["user_id"] == "999"
        assert "User 999" in data["name"]

    @pytest.mark.asyncio
    async def test_userinfo_with_context_logs(self, mock_context):
        """get_user_info() should log access when context available"""
        await get_user_info("123", format="json", ctx=mock_context)

        # Should call debug logging
        mock_context.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_userinfo_without_context_still_works(self):
        """get_user_info() should work without context"""
        result = await get_user_info("123", ctx=None)

        # Should still return valid JSON
        data = json.loads(result)
        assert data["user_id"] == "123"

    @pytest.mark.asyncio
    async def test_userinfo_has_all_fields(self):
        """get_user_info() should include all expected fields"""
        result = await get_user_info("123", format="json")

        data = json.loads(result)

        # Check all required fields
        assert "user_id" in data
        assert "name" in data
        assert "email" in data
        assert "status" in data
        assert "created_at" in data
        assert "last_login" in data


class TestStaticResources:
    """Tests for static resources"""

    def test_get_static_resources_returns_list(self):
        """get_static_resources() should return a list of resources"""
        resources = get_static_resources()
        assert isinstance(resources, list)

    def test_static_resources_not_empty(self):
        """get_static_resources() should return non-empty list"""
        resources = get_static_resources()
        assert len(resources) >= 3  # At least status, features, readme

    def test_static_resources_have_uri(self):
        """Static resources should have URI attribute"""
        resources = get_static_resources()
        for resource in resources:
            assert hasattr(resource, "uri")

    def test_static_resources_have_name(self):
        """Static resources should have name attribute"""
        resources = get_static_resources()
        for resource in resources:
            assert hasattr(resource, "name")

    def test_static_resources_have_description(self):
        """Static resources should have description attribute"""
        resources = get_static_resources()
        for resource in resources:
            assert hasattr(resource, "description")

    def test_status_resource_exists(self):
        """Status resource should exist in list"""
        resources = get_static_resources()
        uris = [str(r.uri) for r in resources]
        assert any("status" in uri for uri in uris)

    def test_features_resource_exists(self):
        """Features resource should exist in list"""
        resources = get_static_resources()
        uris = [str(r.uri) for r in resources]
        assert any("features" in uri for uri in uris)

    def test_readme_resource_exists(self):
        """README resource should exist in list"""
        resources = get_static_resources()
        uris = [str(r.uri) for r in resources]
        assert any("readme" in uri for uri in uris)


class TestDocsResource:
    """Tests for docs wildcard resource"""

    @pytest.mark.asyncio
    async def test_docs_returns_string(self):
        """get_documentation() should return a string"""
        result = await get_documentation("getting-started")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_docs_getting_started(self):
        """get_documentation() should return getting started docs"""
        result = await get_documentation("getting-started")
        assert "Getting Started" in result

    @pytest.mark.asyncio
    async def test_docs_api_tools(self):
        """get_documentation() should return tools documentation"""
        result = await get_documentation("api/tools")
        assert "Tools" in result or "API" in result

    @pytest.mark.asyncio
    async def test_docs_guides_oauth(self):
        """get_documentation() should return OAuth guide"""
        result = await get_documentation("guides/oauth")
        assert "OAuth" in result

    @pytest.mark.asyncio
    async def test_docs_invalid_path(self):
        """get_documentation() should handle invalid path"""
        result = await get_documentation("invalid/nonexistent/path")
        assert "not found" in result.lower() or "not exist" in result.lower()

    @pytest.mark.asyncio
    async def test_docs_empty_path(self):
        """get_documentation() should handle empty path"""
        result = await get_documentation("")
        # Should return something (index or error)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_docs_with_context(self, mock_context):
        """get_documentation() should work with context"""
        result = await get_documentation("test", ctx=mock_context)
        # Should return string result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_docs_without_context(self):
        """get_documentation() should work without context"""
        result = await get_documentation("getting-started", ctx=None)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_docs_nested_paths(self):
        """get_documentation() should handle nested paths"""
        result = await get_documentation("api/resources/types")
        # Should return something
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_docs_not_empty(self):
        """get_documentation() should not return empty string for valid paths"""
        valid_paths = ["getting-started", "api/tools", "guides/oauth"]
        for path in valid_paths:
            result = await get_documentation(path)
            assert len(result) > 0
