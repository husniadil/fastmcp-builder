"""
FastMCP Testing Examples

Comprehensive test examples showing how to test FastMCP servers
using the FastMCP Client for fast, in-memory testing.

Run tests:
    pytest test_examples.py -v

Run with coverage:
    pytest test_examples.py -v --cov=. --cov-report=html

Requirements:
    pip install pytest pytest-asyncio fastmcp
"""

import pytest
from fastmcp import FastMCP, Client


# ============================================================================
# FIXTURES - Setup test server and client
# ============================================================================


@pytest.fixture
def mcp():
    """Create a test server with sample tools and resources"""
    server = FastMCP("test-server")

    # Add sample tool
    @server.tool()
    def ping() -> dict:
        return {"status": "ok", "message": "pong"}

    @server.tool()
    def add_numbers(a: int, b: int) -> dict:
        return {"result": a + b}

    # Module-level counter for stateful testing
    counter_value = [0]  # Use list to avoid global

    @server.tool()
    def counter(action: str = "get") -> dict:
        if action == "increment":
            counter_value[0] += 1
        elif action == "decrement":
            counter_value[0] -= 1
        elif action == "reset":
            counter_value[0] = 0
        return {"count": counter_value[0], "action": action}

    # Add sample resource
    @server.resource("greeting://welcome")
    def get_welcome() -> str:
        return "Welcome to test server!"

    @server.resource("user://{user_id}")
    def get_user(user_id: str) -> str:
        return f"User ID: {user_id}"

    # Add sample prompt
    @server.prompt()
    def explain(topic: str) -> str:
        return f"Please explain {topic} in detail."

    return server


@pytest.fixture
async def client(mcp):
    """Provide FastMCP client for testing"""
    async with Client(mcp) as c:
        yield c


@pytest.fixture
async def reset_counter(client):
    """Reset counter before and after each test"""
    await client.call_tool("counter", {"action": "reset"})
    yield
    await client.call_tool("counter", {"action": "reset"})


# ============================================================================
# TEST EXAMPLES - Basic Connectivity
# ============================================================================


class TestBasicConnectivity:
    """Test basic server connectivity"""

    @pytest.mark.asyncio
    async def test_ping_server(self, client):
        """Should successfully ping the server"""
        result = await client.ping()
        assert result is True

    @pytest.mark.asyncio
    async def test_list_tools(self, client):
        """Should list all registered tools"""
        tools = await client.list_tools()

        tool_names = [tool.name for tool in tools]

        assert "ping" in tool_names
        assert "add_numbers" in tool_names
        assert "counter" in tool_names
        assert len(tools) == 3

    @pytest.mark.asyncio
    async def test_list_resources(self, client):
        """Should list all registered resources"""
        resources = await client.list_resources()

        resource_uris = [str(resource.uri) for resource in resources]

        assert "greeting://welcome" in resource_uris
        # Template resource shows as pattern
        assert any("user://" in uri for uri in resource_uris)

    @pytest.mark.asyncio
    async def test_list_prompts(self, client):
        """Should list all registered prompts"""
        prompts = await client.list_prompts()

        prompt_names = [prompt.name for prompt in prompts]
        assert "explain" in prompt_names


# ============================================================================
# TEST EXAMPLES - Tool Execution
# ============================================================================


class TestToolExecution:
    """Test tool execution via client"""

    @pytest.mark.asyncio
    async def test_call_ping_tool(self, client):
        """Should successfully call ping tool"""
        result = await client.call_tool("ping", {})

        data = result.data
        assert data["status"] == "ok"
        assert data["message"] == "pong"

    @pytest.mark.asyncio
    async def test_call_tool_with_parameters(self, client):
        """Should call tool with parameters"""
        result = await client.call_tool("add_numbers", {"a": 5, "b": 3})

        data = result.data
        assert data["result"] == 8

    @pytest.mark.asyncio
    async def test_tool_with_multiple_calls(self, client):
        """Should handle multiple tool calls"""
        result1 = await client.call_tool("add_numbers", {"a": 10, "b": 20})
        result2 = await client.call_tool("add_numbers", {"a": 5, "b": 7})

        assert result1.data["result"] == 30
        assert result2.data["result"] == 12

    @pytest.mark.asyncio
    async def test_stateful_tool(self, client, reset_counter):
        """Should manage state across calls"""
        # Get initial count (should be 0 after reset)
        result = await client.call_tool("counter", {"action": "get"})
        assert result.data["count"] == 0

        # Increment twice
        await client.call_tool("counter", {"action": "increment"})
        await client.call_tool("counter", {"action": "increment"})

        result = await client.call_tool("counter", {"action": "get"})
        assert result.data["count"] == 2

        # Decrement once
        await client.call_tool("counter", {"action": "decrement"})

        result = await client.call_tool("counter", {"action": "get"})
        assert result.data["count"] == 1

        # Reset
        await client.call_tool("counter", {"action": "reset"})

        result = await client.call_tool("counter", {"action": "get"})
        assert result.data["count"] == 0


# ============================================================================
# TEST EXAMPLES - Resource Reading
# ============================================================================


class TestResourceReading:
    """Test resource reading via client"""

    @pytest.mark.asyncio
    async def test_read_simple_resource(self, client):
        """Should read simple resource"""
        content = await client.read_resource("greeting://welcome")
        assert "Welcome" in content

    @pytest.mark.asyncio
    async def test_read_template_resource(self, client):
        """Should read template resource with parameters"""
        # Read with different IDs
        content1 = await client.read_resource("user://123")
        assert "123" in content1

        content2 = await client.read_resource("user://abc")
        assert "abc" in content2


# ============================================================================
# TEST EXAMPLES - Prompt Generation
# ============================================================================


class TestPrompts:
    """Test prompt generation"""

    @pytest.mark.asyncio
    async def test_generate_prompt(self, client):
        """Should generate prompt from template"""
        prompt = await client.get_prompt("explain", {"topic": "FastMCP"})

        assert len(prompt.messages) > 0
        message = prompt.messages[0]

        assert message.role == "user"
        assert "FastMCP" in message.content.text

    @pytest.mark.asyncio
    async def test_prompt_with_different_parameters(self, client):
        """Should generate different prompts"""
        prompt1 = await client.get_prompt("explain", {"topic": "OAuth"})
        prompt2 = await client.get_prompt("explain", {"topic": "Testing"})

        content1 = prompt1.messages[0].content.text
        content2 = prompt2.messages[0].content.text

        assert "OAuth" in content1
        assert "Testing" in content2
        assert content1 != content2


# ============================================================================
# TEST EXAMPLES - Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, client, reset_counter):
        """Should execute complete workflow across multiple components"""
        # Step 1: Check server health
        ping_result = await client.ping()
        assert ping_result is True

        # Step 2: Read welcome message
        welcome = await client.read_resource("greeting://welcome")
        assert "Welcome" in welcome

        # Step 3: Perform calculation
        calc_result = await client.call_tool("add_numbers", {"a": 10, "b": 5})
        assert calc_result.data["result"] == 15

        # Step 4: Test state management
        await client.call_tool("counter", {"action": "increment"})
        counter_result = await client.call_tool("counter", {"action": "get"})
        assert counter_result.data["count"] == 1

        # Step 5: Generate prompt
        prompt = await client.get_prompt("explain", {"topic": "Workflow"})
        assert "Workflow" in prompt.messages[0].content.text

    @pytest.mark.asyncio
    async def test_list_all_capabilities(self, client):
        """Should list all server capabilities"""
        # List all
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        # Verify we have capabilities
        assert len(tools) > 0
        assert len(resources) > 0
        assert len(prompts) > 0

        # Verify structure
        assert all(hasattr(t, "name") for t in tools)
        assert all(hasattr(r, "uri") for r in resources)
        assert all(hasattr(p, "name") for p in prompts)


# ============================================================================
# TEST EXAMPLES - Error Handling
# ============================================================================


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_tool_with_invalid_parameters(self, client):
        """Should handle invalid parameters gracefully"""
        # This depends on how your tool handles errors
        # For this example, let's assume add_numbers requires integers
        try:
            _result = await client.call_tool("add_numbers", {"a": "invalid", "b": 5})
            # If tool doesn't validate, it might succeed or fail
            # Adjust assertion based on your implementation
        except Exception as e:
            # Expected to fail with validation error
            assert "invalid" in str(e).lower() or "type" in str(e).lower()


# ============================================================================
# TEST EXAMPLES - Advanced Patterns
# ============================================================================


class TestAdvancedPatterns:
    """Advanced testing patterns"""

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, client):
        """Should handle concurrent tool calls"""
        import asyncio

        # Execute multiple calls concurrently
        results = await asyncio.gather(
            client.call_tool("add_numbers", {"a": 1, "b": 1}),
            client.call_tool("add_numbers", {"a": 2, "b": 2}),
            client.call_tool("add_numbers", {"a": 3, "b": 3}),
        )

        assert results[0].data["result"] == 2
        assert results[1].data["result"] == 4
        assert results[2].data["result"] == 6

    @pytest.mark.asyncio
    async def test_resource_access_patterns(self, client):
        """Should support different resource access patterns"""
        # Access multiple resources
        welcome = await client.read_resource("greeting://welcome")
        user = await client.read_resource("user://123")

        assert welcome is not None
        assert user is not None
        assert welcome != user


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    import sys

    pytest.main([__file__, "-v"] + sys.argv[1:])
