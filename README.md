# FastMCP Builder - Claude Code Skill

A comprehensive Claude Code skill for building production-ready MCP (Model Context Protocol) servers using the FastMCP Python framework. This skill provides complete reference implementations, working examples, and proven patterns for creating robust MCP servers with tools, resources, prompts, OAuth authentication, and comprehensive testing.

## What is FastMCP?

**FastMCP** is the official high-level Python framework for building MCP servers. It's simpler, faster to develop with, and more maintainable than the low-level MCP SDK. This skill focuses exclusively on FastMCP-based development.

## What's Included

This skill contains everything you need to build production-ready FastMCP servers:

### 1. Reference Documentation (`reference/`)

Six comprehensive guides covering all aspects of FastMCP development:

- **[fastmcp_overview.md](./reference/fastmcp_overview.md)** - Introduction, when to use FastMCP, key features
- **[project_structure.md](./reference/project_structure.md)** - Recommended structure, file organization, DRY patterns
- **[tool_patterns.md](./reference/tool_patterns.md)** - 6 tool patterns with complete examples
- **[resource_patterns.md](./reference/resource_patterns.md)** - 4 resource types (static, dynamic, template, wildcard)
- **[oauth_integration.md](./reference/oauth_integration.md)** - Complete Google OAuth setup guide
- **[testing_guide.md](./reference/testing_guide.md)** - FastMCP Client testing, patterns, best practices

### 2. Code Examples (`examples/`)

Runnable examples from minimal to complete servers:

- **[minimal_server.py](./examples/minimal_server.py)** - Absolute simplest FastMCP server (28 lines)
- **[complete_server_structure.py](./examples/complete_server_structure.py)** - Full-featured single-file example with all patterns
- **[test_examples.py](./examples/test_examples.py)** - Comprehensive testing examples

### 3. Complete Reference Project (`reference-project/`)

A full production implementation demonstrating best practices:

- **6 production-ready tools** - Various patterns (sync, async, stateful, with context)
- **7 resource instances** - 4 types (static, dynamic, template, wildcard)
- **1 universal prompt** - Reusable prompt template
- **145 passing tests** - Comprehensive test coverage
- **OAuth integration** - Complete Google OAuth setup
- **Dual-mode architecture** - `main.py` (with OAuth) + `main_noauth.py` (local testing)
- **DRY principle** - Uses `common.py` for component registration

## When to Use This Skill

Use this skill when you need to:

- Build MCP servers with FastMCP (Python-based development)
- Add OAuth authentication (especially Google OAuth for remote access)
- Implement production patterns (tools, resources, prompts with best practices)
- Set up comprehensive testing (using FastMCP Client for fast, in-memory tests)
- Structure larger projects (proper organization and separation of concerns)
- Deploy to production (with authentication, error handling, monitoring)

**Don't use this skill for:**

- TypeScript/Node.js MCP servers (use mcp-builder skill instead)
- Low-level MCP protocol work (use MCP SDK directly)
- Non-FastMCP Python servers (this is FastMCP-specific)

## Installation

### Option 1: Install via Plugin Marketplace (Recommended)

1. **Register this marketplace** in Claude Code:

   ```
   /plugin marketplace add husniadil/fastmcp-builder
   ```

2. **Browse and install:**
   - Select "Browse and install plugins"
   - Choose "fastmcp-builder-skill"
   - Select "fastmcp-builder"
   - Click "Install now"

3. **Or install directly:**
   ```
   /plugin install fastmcp-builder@fastmcp-builder-skill
   ```

### Option 2: Manual Installation

Clone or download this repository to your Claude Code skills directory:

```bash
cd ~/.claude/skills
git clone https://github.com/husniadil/fastmcp-builder.git
```

### Using the Skill

Once installed, simply reference the skill in your request:

```
Use the fastmcp-builder skill to create a new MCP server with OAuth authentication
```

## Quick Start

### Simple Example

Create a minimal FastMCP server:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### Try the Included Examples

Navigate to the skill directory and run the examples:

```bash
# Navigate to skill directory
cd ~/.claude/plugins/marketplaces/fastmcp-builder-skill

# Try the minimal server
python examples/minimal_server.py

# Try the complete server structure
python examples/complete_server_structure.py

# Run with HTTP mode
python examples/complete_server_structure.py --http
```

## Building Your First Server

### Phase 1: Planning & Setup

1. **Review FastMCP Overview** - Load `reference/fastmcp_overview.md`
2. **Understand Requirements** - What tools, resources, prompts do you need?
3. **Review Project Structure** - Load `reference/project_structure.md`
4. **Set Up Project** - Create directory structure and install dependencies

```bash
mkdir my-mcp-server && cd my-mcp-server
mkdir -p app/tools app/resources app/prompts tests
uv add fastmcp==2.13.0.1 python-dotenv==1.2.1
uv add --optional test pytest==8.4.2 pytest-asyncio==1.2.0 pytest-mock==3.15.1 httpx==0.28.1
```

### Phase 2: Core Implementation

1. **Implement Configuration** (`app/config.py`) - Environment variables, settings
2. **Implement Tools** (`app/tools/`) - Follow patterns from `reference/tool_patterns.md`
3. **Implement Resources** (`app/resources/`) - Follow patterns from `reference/resource_patterns.md`
4. **Implement Prompts** (`app/prompts/`) - Reusable prompt templates
5. **Create Common Registration** (`app/common.py`) - DRY principle for registering components
6. **Create Server Entry Points** - `main_noauth.py` (local) + `main.py` (OAuth)

### Phase 3: OAuth Integration (Optional)

Follow `reference/oauth_integration.md` for:

1. Setting up Google OAuth credentials
2. Implementing GoogleProvider
3. Testing with ngrok
4. Configuring Claude Desktop

### Phase 4: Testing

Follow `reference/testing_guide.md` for:

1. Setting up test structure (`tests/conftest.py`)
2. Writing tool tests
3. Writing resource tests
4. Writing integration tests
5. Running tests: `uv run pytest tests/ -v`

### Phase 5: Documentation & Deployment

1. Write comprehensive README
2. Create .env.example template
3. Test OAuth flow
4. Deploy to production (Railway, Fly.io, VPS)

## Project Structure

Recommended structure for FastMCP projects:

```
my-mcp-server/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration & environment variables
│   ├── common.py           # Shared component registration (DRY)
│   ├── main.py             # Server with OAuth
│   ├── main_noauth.py      # Server without OAuth (local testing)
│   ├── tools/              # Tool implementations
│   │   ├── __init__.py
│   │   ├── my_tool.py
│   │   └── ...
│   ├── resources/          # Resource implementations
│   │   ├── __init__.py
│   │   ├── static.py
│   │   └── ...
│   └── prompts/            # Prompt templates
│       ├── __init__.py
│       └── explain.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Test fixtures
│   ├── test_tools.py
│   ├── test_resources.py
│   └── test_integration.py
├── pyproject.toml          # Project dependencies
├── .env.example            # Environment variable template
├── .env                    # Actual environment variables (gitignored)
└── README.md
```

## Tool Patterns

This skill includes 6 proven tool patterns:

1. **Basic Sync Tools** - Simple synchronous functions (health checks, queries)
2. **Data Processing Tools** - Text analysis, transformations
3. **Tools with Context** - Logging, progress tracking, better UX
4. **Stateful Tools** - Counters, session management
5. **API Integration Tools** - External service calls
6. **Advanced Async Tools** - Complex workflows, parallel processing

See `reference/tool_patterns.md` for complete examples.

## Resource Patterns

This skill includes 4 resource types:

1. **Static Resources** - Fixed content (status, features, documentation)
2. **Dynamic Resources** - Generated content (current time, computed data)
3. **Template Resources** - Path parameters (`user://{user_id}`)
4. **Wildcard Resources** - Multi-segment paths (`docs://{path*}`)

See `reference/resource_patterns.md` for complete examples.

## OAuth Integration

Complete guide for adding Google OAuth authentication:

- Setting up Google Cloud Console
- Implementing GoogleProvider
- Testing with ngrok
- Configuring Claude Desktop Connectors
- Production deployment considerations

See `reference/oauth_integration.md` for the complete guide.

## Testing

Comprehensive testing guide using FastMCP Client:

- Fast, in-memory testing (no server startup required)
- Tool testing patterns
- Resource testing patterns
- Integration testing patterns
- Achieving >80% test coverage

See `reference/testing_guide.md` for complete examples.

## Best Practices

1. **Use FastMCP** - Simpler than MCP SDK for most use cases
2. **Follow project structure** - Use `common.py` pattern (DRY principle)
3. **Dual-mode servers** - `main.py` (OAuth) + `main_noauth.py` (local)
4. **Comprehensive testing** - Use FastMCP Client, aim for >80% coverage
5. **Clear documentation** - Docstrings, README, usage examples
6. **Error handling** - Graceful failures, informative error messages
7. **Context usage** - Logging, progress for better UX
8. **Security** - Environment variables, never commit secrets

## Common Workflows

### Creating a New Tool

1. Create `app/tools/my_tool.py`
2. Implement tool function
3. Add to `app/common.py` registration
4. Write tests in `tests/test_tools.py`
5. Run tests: `uv run pytest tests/test_tools.py -v`

### Adding OAuth

1. Review `reference/oauth_integration.md`
2. Set up Google OAuth credentials
3. Update `app/config.py` with OAuth settings
4. Modify `app/main.py` to use GoogleProvider
5. Test with ngrok
6. Configure Claude Desktop Connectors

### Debugging

1. Use `main_noauth.py` for faster local testing
2. Add logging with Context: `await ctx.debug(...)`
3. Write tests to isolate issues
4. Check tool/resource registration in `common.py`
5. Verify environment variables loaded

## Reference Project Details

The `reference-project/` directory contains a complete production implementation:

- **Name:** `mcp-auth-demo`
- **Version:** 1.0.0
- **Tools:** 6 (ping, counter, process_text, analyze_text, get_forecast, request_info)
- **Resources:** 7 instances across 4 types
- **Prompts:** 1 universal prompt template
- **Tests:** 145 passing tests with comprehensive coverage
- **Features:** OAuth, dual-mode architecture, DRY principle, comprehensive error handling

Use this as a reference when building your own servers.

## Additional Resources

- **FastMCP Documentation:** https://gofastmcp.com/
- **FastMCP GitHub:** https://github.com/jlowin/fastmcp
- **MCP Specification:** https://modelcontextprotocol.io/
- **Google OAuth Guide:** https://developers.google.com/identity/protocols/oauth2
- **Claude Code Skills:** https://docs.claude.com/en/docs/claude-code/skills.md

## Requirements

- Python 3.11+
- FastMCP 2.13.0.1
- python-dotenv 1.2.1

For testing:

- pytest 8.4.2
- pytest-asyncio 1.2.0
- pytest-mock 3.15.1
- httpx 0.28.1

## Contributing

This is a Claude Code skill. To contribute:

1. Test changes with the reference project
2. Ensure all examples run successfully
3. Update documentation as needed
4. Add tests for new patterns

## License

MIT License - Copyright 2025 Husni Adil Makmur

This skill is provided as-is for use with Claude Code. See [LICENSE](./LICENSE) file for details.

The FastMCP framework itself is licensed separately - see the [FastMCP repository](https://github.com/jlowin/fastmcp) for details.

## Notes

- This skill focuses on **FastMCP**, not the low-level MCP SDK
- All examples use **Python 3.11+**
- OAuth examples use **Google OAuth** (other providers possible)
- Testing uses **FastMCP Client** (in-memory, fast)
- Deployment examples are production-ready

Happy building!
