"""
End-to-End Tests using FastMCP Client

Tests the complete MCP server functionality using fastmcp.Client
with in-memory transport for fast, deterministic testing.
"""

import pytest
from fastmcp import Client
from app.main_noauth import mcp  # Use no-auth version for testing


class TestBasicConnectivity:
    """Test basic server connectivity"""

    @pytest.mark.asyncio
    async def test_ping_server(self):
        """Should successfully ping the server"""
        async with Client(mcp) as client:
            result = await client.ping()
            assert result is True

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Should list all registered tools"""
        async with Client(mcp) as client:
            tools = await client.list_tools()

            # Should have all 6 production tools
            tool_names = [tool.name for tool in tools]

            assert "ping" in tool_names
            assert "analyze_text" in tool_names
            assert "process_text" in tool_names
            assert "counter" in tool_names
            assert "get_request_info" in tool_names
            assert "get_forecast" in tool_names

            # Should have exactly 6 tools
            assert len(tools) == 6

    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Should list all registered resources"""
        async with Client(mcp) as client:
            resources = await client.list_resources()

            # Should have all our resources
            resource_uris = [str(resource.uri) for resource in resources]

            # Dynamic resources
            assert "greeting://welcome" in resource_uris

            # Static resources
            assert "text://status" in resource_uris
            assert "text://features" in resource_uris
            # File resources have trailing slash
            assert any("file://readme" in uri for uri in resource_uris)

    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Should list all registered prompts"""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()

            # Should have our universal prompt
            prompt_names = [prompt.name for prompt in prompts]
            assert "explain_concept" in prompt_names


class TestToolExecution:
    """Test tool execution via client"""

    @pytest.mark.asyncio
    async def test_call_ping_tool(self):
        """Should successfully call ping tool"""
        async with Client(mcp) as client:
            result = await client.call_tool("ping", {})

            # Parse the result
            data = result.data
            assert data["status"] == "ok"
            assert data["message"] == "pong"
            assert "timestamp" in data
            assert "response_time_ms" in data

    @pytest.mark.asyncio
    async def test_call_counter_tool(self):
        """Should successfully manage counter state"""
        async with Client(mcp) as client:
            # Get initial count (should be 0 or previous value)
            result = await client.call_tool("counter", {"action": "get"})
            initial_count = result.data["count"]

            # Increment
            result = await client.call_tool("counter", {"action": "increment"})
            assert result.data["count"] == initial_count + 1
            assert result.data["action"] == "increment"

            # Increment again
            result = await client.call_tool("counter", {"action": "increment"})
            assert result.data["count"] == initial_count + 2

            # Get current count
            result = await client.call_tool("counter", {"action": "get"})
            assert result.data["count"] == initial_count + 2

            # Decrement
            result = await client.call_tool("counter", {"action": "decrement"})
            assert result.data["count"] == initial_count + 1

    @pytest.mark.asyncio
    async def test_call_analyze_text_tool(self):
        """Should analyze text successfully"""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "analyze_text", {"text": "Hello world! This is a test."}
            )

            data = result.data
            assert data["status"] == "completed"
            assert "statistics" in data

            # Check statistics fields
            stats = data["statistics"]
            assert stats["characters"] > 0
            assert stats["words"] > 0
            assert stats["sentences"] > 0

    @pytest.mark.asyncio
    async def test_call_process_text_tool(self):
        """Should process text with analysis"""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "process_text",
                {
                    "content": "I love this demo! It's amazing!",
                    "analysis_type": "sentiment",
                },
            )

            data = result.data
            assert data["status"] == "completed"
            assert "analysis" in data
            assert "features_demonstrated" in data

            # Should demonstrate logging and progress
            features = data["features_demonstrated"]
            assert "logging" in features
            assert "progress" in features

    @pytest.mark.asyncio
    async def test_call_get_request_info_tool(self):
        """Should get request metadata"""
        async with Client(mcp) as client:
            result = await client.call_tool("get_request_info", {})

            data = result.data
            assert data["status"] == "success"
            assert "request" in data
            assert "server" in data

            # Check request metadata
            request = data["request"]
            assert "request_id" in request
            assert "client_id" in request

    @pytest.mark.asyncio
    async def test_call_get_forecast_tool(self):
        """Should get weather forecast"""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "get_forecast", {"city": "Tokyo", "days": 5}
            )

            data = result.data
            assert data["status"] == "success"
            assert data["city"] == "Tokyo"
            assert data["forecast_days"] == 5
            assert "forecast" in data
            assert len(data["forecast"]) == 5

            # Check forecast structure
            forecast_day = data["forecast"][0]
            assert "date" in forecast_day
            assert "temperature" in forecast_day
            assert "condition" in forecast_day


class TestResourceReading:
    """Test resource reading via client"""

    @pytest.mark.asyncio
    async def test_read_welcome_resource(self):
        """Should read welcome message resource"""
        async with Client(mcp) as client:
            result = await client.read_resource("greeting://welcome")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert "Welcome" in content.text
            assert "MCP Auth Demo" in content.text

    @pytest.mark.asyncio
    async def test_read_status_resource(self):
        """Should read static status resource"""
        async with Client(mcp) as client:
            result = await client.read_resource("text://status")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert "operational" in content.text.lower()

    @pytest.mark.asyncio
    async def test_read_features_resource(self):
        """Should read static features resource"""
        async with Client(mcp) as client:
            result = await client.read_resource("text://features")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert "Features" in content.text

    @pytest.mark.asyncio
    async def test_read_readme_resource(self):
        """Should read README file resource"""
        async with Client(mcp) as client:
            result = await client.read_resource("file://readme")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert "MCP Auth Demo" in content.text

    @pytest.mark.asyncio
    async def test_read_userinfo_resource_json(self):
        """Should read userinfo template resource with JSON format"""
        async with Client(mcp) as client:
            result = await client.read_resource("userinfo://123")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert "123" in content.text
            assert "user_id" in content.text

    @pytest.mark.asyncio
    async def test_read_docs_wildcard_resource(self):
        """Should read docs wildcard resource"""
        async with Client(mcp) as client:
            # Test getting-started docs
            result = await client.read_resource("docs://getting-started")
            assert len(result) > 0
            content = result[0]
            assert "Getting Started" in content.text

            # Test api/tools docs
            result = await client.read_resource("docs://api/tools")
            assert len(result) > 0
            content = result[0]
            assert "Tools" in content.text

            # Test guides/oauth docs
            result = await client.read_resource("docs://guides/oauth")
            assert len(result) > 0
            content = result[0]
            assert "OAuth" in content.text

    @pytest.mark.asyncio
    async def test_read_docs_wildcard_invalid_path(self):
        """Should handle invalid docs path gracefully"""
        async with Client(mcp) as client:
            result = await client.read_resource("docs://invalid/path")

            # Result is a list of contents
            assert len(result) > 0
            content = result[0]
            assert (
                "not found" in content.text.lower()
                or "not exist" in content.text.lower()
            )


class TestPromptRendering:
    """Test prompt rendering via client"""

    @pytest.mark.asyncio
    async def test_get_explain_concept_prompt(self):
        """Should render explain_concept prompt"""
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "explain_concept",
                {
                    "concept": "OAuth 2.0",
                    "audience_level": "intermediate",
                    "include_examples": True,
                },
            )

            # Should return prompt with messages
            assert len(result.messages) > 0

            # Check first message content
            message = result.messages[0]
            assert "OAuth 2.0" in message.content.text
            assert "intermediate" in message.content.text.lower()


class TestStateManagement:
    """Test state persistence across multiple calls"""

    @pytest.mark.asyncio
    async def test_counter_state_persists(self):
        """Counter should maintain state across multiple calls"""
        async with Client(mcp) as client:
            # Reset counter first
            await client.call_tool("counter", {"action": "reset"})

            # Verify it's at 0
            result = await client.call_tool("counter", {"action": "get"})
            assert result.data["count"] == 0

            # Increment 5 times
            for i in range(5):
                result = await client.call_tool("counter", {"action": "increment"})
                assert result.data["count"] == i + 1

            # Verify final count
            result = await client.call_tool("counter", {"action": "get"})
            assert result.data["count"] == 5

            # Decrement 2 times
            for i in range(2):
                result = await client.call_tool("counter", {"action": "decrement"})
                assert result.data["count"] == 4 - i

            # Verify final count
            result = await client.call_tool("counter", {"action": "get"})
            assert result.data["count"] == 3


class TestErrorHandling:
    """Test error handling in various scenarios"""

    @pytest.mark.asyncio
    async def test_call_tool_with_invalid_action(self):
        """Should handle invalid counter action gracefully"""
        async with Client(mcp) as client:
            result = await client.call_tool("counter", {"action": "invalid"})

            data = result.data
            assert data["status"] == "error"
            assert "error" in data
            assert "valid_actions" in data

    @pytest.mark.asyncio
    async def test_call_tool_with_missing_params(self):
        """Should handle missing required parameters"""
        async with Client(mcp) as client:
            # analyze_text requires 'text' parameter
            with pytest.raises(Exception):  # Should raise validation error
                await client.call_tool("analyze_text", {})


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Should execute a complete workflow successfully"""
        async with Client(mcp) as client:
            # 1. Ping server
            ping_result = await client.ping()
            assert ping_result is True

            # 2. List available tools
            tools = await client.list_tools()
            assert len(tools) > 0

            # 3. Read welcome resource
            welcome = await client.read_resource("greeting://welcome")
            assert len(welcome) > 0

            # 4. Process some text
            text_result = await client.call_tool(
                "process_text",
                {"content": "Testing complete workflow!", "analysis_type": "summary"},
            )
            assert text_result.data["status"] == "completed"

            # 5. Check request info
            info_result = await client.call_tool("get_request_info", {})
            assert info_result.data["status"] == "success"

            # 6. Increment counter
            counter_result = await client.call_tool("counter", {"action": "increment"})
            assert counter_result.data["status"] == "success"

            # 7. Get forecast
            forecast_result = await client.call_tool(
                "get_forecast", {"city": "Jakarta", "days": 3}
            )
            assert forecast_result.data["status"] == "success"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_calls(self):
        """Should handle multiple operations correctly"""
        async with Client(mcp) as client:
            # Reset counter
            await client.call_tool("counter", {"action": "reset"})

            # Make multiple calls in sequence
            results = []
            for _ in range(3):
                result = await client.call_tool("counter", {"action": "increment"})
                results.append(result.data["count"])

            # Verify incremental counts
            assert results == [1, 2, 3]
