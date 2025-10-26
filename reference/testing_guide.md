# FastMCP Testing Guide

Comprehensive guide to testing FastMCP servers using the FastMCP Client for fast, deterministic, in-memory testing.

## Why FastMCP Client Testing?

**FastMCP Client** provides in-memory testing without network:

**✅ Advantages:**

- **Fast**: No network overhead, runs in milliseconds
- **Deterministic**: No flaky network issues
- **Isolated**: No external dependencies
- **Production-like**: Uses same protocol as real clients
- **CI/CD friendly**: Works in any environment

**vs Traditional Testing:**

- ❌ STDIO testing: Requires spawning processes, slower
- ❌ HTTP testing: Requires running server, network calls
- ❌ Manual testing: Time-consuming, not repeatable

## Setup

### Installation

```bash
# Install test dependencies
uv add --optional test pytest pytest-asyncio pytest-mock httpx

# or with pip
pip install pytest pytest-asyncio pytest-mock httpx
```

### Project Structure

```
my-mcp-server/
├── app/
│   ├── main.py
│   └── main_noauth.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_client.py       # End-to-end tests
│   ├── test_tools.py        # Unit tests for tools
│   ├── test_resources.py    # Unit tests for resources
│   └── test_prompts.py      # Unit tests for prompts
└── pyproject.toml
```

### pyproject.toml Configuration

```toml
[project.optional-dependencies]
test = [
    "pytest==8.4.2",
    "pytest-asyncio==1.2.0",
    "pytest-mock==3.15.1",
    "httpx==0.28.1",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "integration: Integration tests (require running server)",
]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
```

## FastMCP Client Basics

### Basic Usage

```python
import pytest
from fastmcp import Client
from app.main_noauth import mcp  # Import the server instance


@pytest.mark.asyncio
async def test_basic_client():
    """Test basic client connectivity"""
    async with Client(mcp) as client:
        # Ping the server
        result = await client.ping()
        assert result is True

        # List tools
        tools = await client.list_tools()
        assert len(tools) > 0

        # Call a tool
        result = await client.call_tool("ping", {})
        assert result.data["status"] == "ok"
```

**Key Points:**

- Import server from `main_noauth.py` (no OAuth for testing)
- Use `async with Client(mcp)` context manager
- Client provides methods: `ping()`, `list_tools()`, `call_tool()`, etc.

## Test Patterns

### 1. Connectivity Tests

Test basic server connectivity:

```python
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

            tool_names = [tool.name for tool in tools]

            # Best practice: Check for specific tools your server implements
            assert "ping" in tool_names
            assert "analyze_text" in tool_names

            # Then verify total count matches YOUR server's tool count
            # (Reference-project has 6 tools; adjust this number for your server)
            assert len(tools) == 6

    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Should list all registered resources"""
        async with Client(mcp) as client:
            resources = await client.list_resources()

            resource_uris = [str(resource.uri) for resource in resources]

            assert "greeting://welcome" in resource_uris
            assert "text://status" in resource_uris

    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Should list all registered prompts"""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()

            prompt_names = [prompt.name for prompt in prompts]
            assert "explain_concept" in prompt_names
```

### 2. Tool Execution Tests

Test individual tools:

```python
class TestToolExecution:
    """Test tool execution via client"""

    @pytest.mark.asyncio
    async def test_call_ping_tool(self):
        """Should successfully call ping tool"""
        async with Client(mcp) as client:
            result = await client.call_tool("ping", {})

            data = result.data
            assert data["status"] == "ok"
            assert data["message"] == "pong"
            assert "timestamp" in data
            assert "response_time_ms" in data

    @pytest.mark.asyncio
    async def test_analyze_text_tool(self):
        """Should analyze text and return statistics"""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "analyze_text",
                {"text": "Hello world! This is a test."}
            )

            data = result.data
            assert data["status"] == "completed"
            assert "statistics" in data
            assert data["statistics"]["words"] > 0

    @pytest.mark.asyncio
    async def test_counter_tool_state(self):
        """Should manage counter state across calls"""
        async with Client(mcp) as client:
            # Get initial count
            result = await client.call_tool("counter", {"action": "get"})
            initial_count = result.data["count"]

            # Increment
            result = await client.call_tool("counter", {"action": "increment"})
            assert result.data["count"] == initial_count + 1

            # Increment again
            result = await client.call_tool("counter", {"action": "increment"})
            assert result.data["count"] == initial_count + 2

            # Decrement
            result = await client.call_tool("counter", {"action": "decrement"})
            assert result.data["count"] == initial_count + 1

            # Reset
            result = await client.call_tool("counter", {"action": "reset"})
            assert result.data["count"] == 0

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Should handle invalid tool calls gracefully"""
        async with Client(mcp) as client:
            # Invalid action for counter
            result = await client.call_tool("counter", {"action": "invalid"})
            assert result.data["status"] == "error"
            assert "error" in result.data
```

### 3. Resource Reading Tests

Test resource access:

```python
class TestResourceReading:
    """Test resource reading via client"""

    @pytest.mark.asyncio
    async def test_read_static_text_resource(self):
        """Should read static text resource"""
        async with Client(mcp) as client:
            content = await client.read_resource("text://status")
            assert "operational" in content.lower()

    @pytest.mark.asyncio
    async def test_read_dynamic_resource(self):
        """Should read dynamic resource"""
        async with Client(mcp) as client:
            content = await client.read_resource("greeting://welcome")
            assert "Welcome" in content

    @pytest.mark.asyncio
    async def test_read_template_resource(self):
        """Should read template resource with parameters"""
        async with Client(mcp) as client:
            # JSON format (default)
            content = await client.read_resource("userinfo://123")
            assert "user123@example.com" in content

            # XML format
            content = await client.read_resource("userinfo://123?format=xml")
            assert "<user>" in content

            # Text format
            content = await client.read_resource("userinfo://123?format=text")
            assert "User Information" in content

    @pytest.mark.asyncio
    async def test_read_wildcard_resource(self):
        """Should read wildcard resource"""
        async with Client(mcp) as client:
            # Single segment
            content = await client.read_resource("docs://getting-started")
            assert "Getting Started" in content

            # Multiple segments
            content = await client.read_resource("docs://api/tools")
            assert "Tools" in content
```

### 4. Prompt Tests

Test prompt generation:

```python
class TestPrompts:
    """Test prompt generation"""

    @pytest.mark.asyncio
    async def test_explain_concept_prompt(self):
        """Should generate explanation prompt"""
        async with Client(mcp) as client:
            prompt = await client.get_prompt(
                "explain_concept",
                {
                    "concept": "OAuth 2.0",
                    "audience_level": "intermediate",
                    "include_examples": True
                }
            )

            # Check prompt structure
            assert len(prompt.messages) > 0
            message = prompt.messages[0]
            assert message.role == "user"

            # Check content
            content = message.content.text
            assert "OAuth 2.0" in content
            assert "intermediate" in content

    @pytest.mark.asyncio
    async def test_prompt_with_defaults(self):
        """Should use default parameters"""
        async with Client(mcp) as client:
            prompt = await client.get_prompt(
                "explain_concept",
                {"concept": "FastMCP"}
            )

            content = prompt.messages[0].content.text
            assert "FastMCP" in content
```

## Test Fixtures (conftest.py)

Create reusable fixtures:

```python
# tests/conftest.py

import pytest
from fastmcp import Client
from app.main_noauth import mcp


@pytest.fixture
async def client():
    """Provide FastMCP client for testing"""
    async with Client(mcp) as c:
        yield c


@pytest.fixture
async def reset_counter(client):
    """Reset counter before each test"""
    await client.call_tool("counter", {"action": "reset"})
    yield
    # Cleanup after test
    await client.call_tool("counter", {"action": "reset"})


# Usage in tests:
@pytest.mark.asyncio
async def test_with_client(client):
    """Test using client fixture"""
    result = await client.ping()
    assert result is True


@pytest.mark.asyncio
async def test_counter_reset(client, reset_counter):
    """Test with counter reset"""
    result = await client.call_tool("counter", {"action": "get"})
    assert result.data["count"] == 0
```

## Integration Tests

Test complete workflows:

```python
class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_text_processing_workflow(self):
        """Should process text through multiple tools"""
        async with Client(mcp) as client:
            text = "This is a sample text for testing. It has multiple sentences."

            # Step 1: Analyze text
            analysis = await client.call_tool("analyze_text", {"text": text})
            assert analysis.data["status"] == "completed"
            word_count = analysis.data["statistics"]["words"]

            # Step 2: Process text
            process = await client.call_tool(
                "process_text",
                {"content": text, "analysis_type": "summary"}
            )
            assert process.data["status"] == "completed"

            # Step 3: Verify results consistent
            assert process.data["analysis"]["words"] == word_count

    @pytest.mark.asyncio
    async def test_resource_documentation_workflow(self):
        """Should navigate documentation resources"""
        async with Client(mcp) as client:
            # Read main welcome
            welcome = await client.read_resource("greeting://welcome")
            assert "Welcome" in welcome

            # Read docs overview
            docs = await client.read_resource("docs://getting-started")
            assert "Quick Start" in docs

            # Read API docs
            api_docs = await client.read_resource("docs://api/tools")
            assert "Tools" in api_docs
```

## Running Tests

### Run All Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py -v

# Run specific test
uv run pytest tests/test_client.py::TestToolExecution::test_call_ping_tool -v
```

### Run with Markers

```bash
# Run only integration tests
uv run pytest tests/ -v -m integration

# Skip integration tests
uv run pytest tests/ -v -m "not integration"
```

## Best Practices

### 1. Test Isolation

Each test should be independent:

```python
# ✅ Good: Each test is independent
@pytest.mark.asyncio
async def test_counter_increment(client, reset_counter):
    """Test starts with clean state"""
    result = await client.call_tool("counter", {"action": "increment"})
    assert result.data["count"] == 1

# ❌ Bad: Depends on other tests
@pytest.mark.asyncio
async def test_counter_value(client):
    """This will fail if run in different order"""
    result = await client.call_tool("counter", {"action": "get"})
    assert result.data["count"] == 5  # Assumes previous tests ran
```

### 2. Clear Assertions

Use descriptive assertions:

```python
# ✅ Good: Clear what's being tested
assert result.data["status"] == "ok", "Health check should return ok status"
assert len(tools) == 6, f"Expected 6 tools (adjust for your server), got {len(tools)}"

# ❌ Bad: Unclear failures
assert result.data
assert tools
```

### 3. Test Both Success and Failure

```python
# Test success case
@pytest.mark.asyncio
async def test_valid_input(client):
    result = await client.call_tool("analyze_text", {"text": "Hello"})
    assert result.data["status"] == "completed"

# Test failure case
@pytest.mark.asyncio
async def test_invalid_input(client):
    result = await client.call_tool("counter", {"action": "invalid"})
    assert result.data["status"] == "error"
    assert "error" in result.data
```

### 4. Use Fixtures for Setup/Teardown

```python
@pytest.fixture
async def sample_data(client):
    """Set up test data"""
    # Setup
    await client.call_tool("create_data", {"name": "test"})

    yield "test"  # Provide to test

    # Teardown
    await client.call_tool("delete_data", {"name": "test"})
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --extra test

      - name: Run tests
        run: uv run pytest tests/ -v --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Debugging Tests

### Print Debug Info

```python
@pytest.mark.asyncio
async def test_debug(client, capsys):
    """Test with debug output"""
    result = await client.call_tool("ping", {})

    # Print for debugging
    print(f"Result: {result.data}")

    # Capture output
    captured = capsys.readouterr()
    print(captured.out)
```

### Use pytest -s

```bash
# Show print statements
uv run pytest tests/test_client.py::test_debug -v -s
```

## Summary

| Test Type             | Purpose            | Example               |
| --------------------- | ------------------ | --------------------- |
| **Connectivity**      | Server basics      | ping, list_tools      |
| **Tool Execution**    | Individual tools   | call_tool with params |
| **Resource Reading**  | Resource access    | read_resource         |
| **Prompt Generation** | Prompt templates   | get_prompt            |
| **Integration**       | Complete workflows | Multi-step operations |

**Key Takeaways:**

- ✅ Use FastMCP Client for fast, in-memory testing
- ✅ Test from `main_noauth.py` (no OAuth needed)
- ✅ Write unit tests for each tool/resource/prompt
- ✅ Add integration tests for workflows
- ✅ Use fixtures for setup/teardown
- ✅ Run tests in CI/CD

Happy testing! 🧪
