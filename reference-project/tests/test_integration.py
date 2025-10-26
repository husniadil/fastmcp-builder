"""
Integration tests for MCP server

These tests require a running server instance.
Run with: pytest tests/test_integration.py -v

Note: Start server in another terminal first:
  ./run.sh --http
"""

import pytest
import httpx


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


BASE_URL = "http://localhost:8000"


class TestServerStartup:
    """Tests for server startup and basic connectivity"""

    @pytest.mark.asyncio
    async def test_server_is_running(self):
        """Server should be accessible"""
        try:
            async with httpx.AsyncClient() as client:
                # Try to connect to any endpoint
                response = await client.get(f"{BASE_URL}/", timeout=5.0)

                # Server should respond (any status code means it's running)
                assert response.status_code in [200, 404, 405]

        except httpx.ConnectError:
            pytest.skip("Server not running. Start with: ./run.sh --http")


class TestOAuthEndpoints:
    """Tests for OAuth proxy endpoints"""

    @pytest.mark.asyncio
    async def test_oauth_metadata_endpoint(self):
        """OAuth metadata endpoint should be accessible"""
        metadata_url = f"{BASE_URL}/.well-known/oauth-authorization-server"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(metadata_url, timeout=5.0)

                assert response.status_code == 200

                # Should return JSON
                data = response.json()
                assert isinstance(data, dict)

                # Should have OAuth metadata fields
                assert "authorization_endpoint" in data
                assert "token_endpoint" in data

        except httpx.ConnectError:
            pytest.skip("Server not running. Start with: ./run.sh --http")

    @pytest.mark.asyncio
    async def test_registration_endpoint(self):
        """Dynamic client registration endpoint should work"""
        register_url = f"{BASE_URL}/register"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    register_url,
                    json={
                        "client_name": "Test Client",
                        "redirect_uris": ["http://localhost:5173/callback"],
                    },
                    timeout=5.0,
                )

                # Should accept registration
                assert response.status_code in [200, 201]

                # Should return client credentials
                data = response.json()
                assert "client_id" in data

        except httpx.ConnectError:
            pytest.skip("Server not running. Start with: ./run.sh --http")


class TestMCPEndpoint:
    """Tests for MCP protocol endpoint"""

    @pytest.mark.asyncio
    async def test_mcp_endpoint_exists(self):
        """MCP endpoint should be accessible"""
        mcp_url = f"{BASE_URL}/mcp/"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(mcp_url, timeout=5.0)

                # Should respond (307 redirect is normal, also accept auth/method errors)
                assert response.status_code in [200, 307, 401, 403, 405]

        except httpx.ConnectError:
            pytest.skip("Server not running. Start with: ./run.sh --http")


class TestFullIntegration:
    """
    Full integration tests (manual testing recommended)

    These tests are placeholders - use MCP Inspector for full OAuth testing
    """

    @pytest.mark.asyncio
    async def test_full_oauth_flow(self):
        """
        Test full OAuth flow (requires manual interaction)

        This is a placeholder for manual OAuth flow testing.
        In practice, you would use MCP Inspector for this.
        """
        # This test is a placeholder
        # Real OAuth flow testing requires browser interaction
        # Use MCP Inspector for manual testing
        pytest.skip("Use MCP Inspector for full OAuth flow testing")
