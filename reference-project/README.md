# MCP Auth Demo

**A minimal, production-ready MCP server with Google OAuth demonstrating all core FastMCP features.**

Built with [FastMCP](https://gofastmcp.com/) - the easiest way to build Model Context Protocol servers in Python.

---

## ✨ Features

- **Google OAuth 2.0** - Secure authentication for remote access
- **6 Production Tools** - Health check, text processing, state management, API integration
- **4 Resource Types, 7 Resource Instances** - Dynamic, static, template, and wildcard resources
- **Universal Prompts** - Reusable prompt templates
- **Clean Architecture** - Modular, maintainable, extensible
- **Full Test Coverage** - 145 passing tests with FastMCP Client integration

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud account (for OAuth)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-auth-demo
cd mcp-auth-demo

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Google OAuth credentials
```

### Run Locally (No Auth)

```bash
# STDIO mode (for Claude Desktop local)
uv run python -m app.main_noauth

# HTTP mode (for testing, runs on port 8000)
uv run python -m app.main_noauth --http
```

### Run with OAuth + ngrok

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Start server with ngrok URL
uv run python -m app.main --http --base-url https://YOUR-NGROK-URL.ngrok-free.app
```

---

## 📦 What's Included

### 6 Production Tools

| Tool               | Description             | Features                                                                            |
| ------------------ | ----------------------- | ----------------------------------------------------------------------------------- |
| `ping`             | Health check            | Basic connectivity test                                                             |
| `analyze_text`     | Text statistics         | Character, word, sentence counts                                                    |
| `process_text`     | Advanced text processor | Logging + progress tracking                                                         |
| `counter`          | State management        | Session-persistent counter (single-process only, resets on restart)                 |
| `get_request_info` | Request metadata        | Request ID, client ID, session info                                                 |
| `get_forecast`     | Weather forecast        | Mock weather API with temperature, conditions, humidity (1-7 days, randomized data) |

### 4 Resource Types (7 Instances)

| Type     | URI                             | Description                                |
| -------- | ------------------------------- | ------------------------------------------ |
| Dynamic  | `greeting://welcome`            | Welcome message                            |
| Template | `userinfo://{user_id}{?format}` | User info (json/xml/text formats)          |
| Wildcard | `docs://{path*}`                | Documentation pages                        |
| Static   | `text://status`                 | Server operational status                  |
| Static   | `text://features`               | Feature list                               |
| Static   | `file://readme`                 | Project README                             |
| Static   | `file://test-results`           | Test results (conditional, if file exists) |

**Note:** The `{?format}` notation indicates an optional query parameter. In code, this is registered as `userinfo://{user_id}` with `format` as a function parameter that FastMCP automatically maps to query parameters.

### 1 Universal Prompt

- `explain_concept` - Technical concept explainer with audience-level customization

---

## 🔧 Google OAuth Setup

### 1. Create OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Type: **Web application**
4. Add redirect URI: `https://YOUR-NGROK-URL.ngrok-free.app/auth/callback`

⚠️ **Important:** Only add YOUR server's callback URI, not Claude Desktop's callback. FastMCP acts as OAuth proxy.

### 2. Configure .env

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
BASE_URL=http://localhost:8000  # or your production URL
```

### 3. Start with ngrok

```bash
# Terminal 1: Start ngrok
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123xyz789.ngrok-free.app)

# Terminal 2: Start server
uv run python -m app.main --http --base-url https://abc123xyz789.ngrok-free.app
```

### 4. Configure Claude Desktop

#### Option A: Local Development (STDIO, No Auth)

For local testing without OAuth, add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-auth-demo-local": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-auth-demo",
        "run",
        "python",
        "-m",
        "app.main_noauth"
      ]
    }
  }
}
```

Replace `/path/to/mcp-auth-demo` with your actual project path.

#### Option B: Remote Access (HTTP with OAuth)

**Requirements:**

- Claude Desktop with Connectors support
- Claude Pro, Max, Team, or Enterprise plan
- Running server with ngrok (see step 3 above)

**Setup Steps:**

1. Open Claude Desktop
2. Go to **Settings > Connectors**
3. Click **"Add custom connector"**
4. Enter your ngrok URL: `https://abc123xyz789.ngrok-free.app`
5. Claude will handle OAuth authentication automatically

**Note:** Remote HTTP servers CANNOT be configured via `claude_desktop_config.json`. You MUST use the Connectors UI.

---

## 📚 Project Structure

```
mcp-auth-demo/
├── app/
│   ├── __init__.py
│   ├── common.py              # Shared registration logic
│   ├── config.py              # Configuration management
│   ├── main.py                # Server with OAuth
│   ├── main_noauth.py         # Server without OAuth (local testing)
│   ├── tools/                 # 6 production tools
│   │   ├── ping.py
│   │   ├── analyze_text.py
│   │   ├── process_text.py
│   │   ├── counter.py
│   │   ├── request_info.py
│   │   └── get_forecast.py
│   ├── resources/             # 4 types of resources
│   │   ├── welcome.py         # Dynamic
│   │   ├── userinfo.py        # Template
│   │   ├── static.py          # Static
│   │   └── docs.py            # Wildcard
│   └── prompts/               # Reusable prompts
│       └── explain.py
├── tests/                     # Full test coverage
│   ├── test_client.py         # FastMCP Client integration tests
│   ├── test_tools.py
│   ├── test_resources.py
│   ├── test_prompts.py
│   └── test_integration.py
├── .env.example               # Environment template
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

---

## 🧪 Testing

### Run All Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_client.py -v

# With coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

```
✅ 145 tests passing
✅ 6 tools tested
✅ 4 resources tested
✅ 1 prompt tested
✅ FastMCP Client integration tested
✅ State management tested
✅ Error handling tested
```

### FastMCP Client Testing

The project includes comprehensive end-to-end tests using FastMCP's in-memory client:

```python
from fastmcp import Client
from app.main_noauth import mcp

async with Client(mcp) as client:
    # Test tools
    result = await client.call_tool("ping", {})

    # Test resources
    content = await client.read_resource("greeting://welcome")

    # Test prompts
    prompt = await client.get_prompt("explain_concept", {...})
```

**Benefits:**

- ⚡ Fast (no network)
- 🎯 Deterministic
- 🔒 Isolated
- 🧪 Production-like

---

## 💡 Usage Examples

### Example 1: Call a Tool

```python
# Ping server
result = await client.call_tool("ping", {})
# {"status": "ok", "message": "pong", ...}

# Get weather forecast
result = await client.call_tool("get_forecast", {
    "city": "Tokyo",
    "days": 5
})
# {"status": "success", "forecast": [...]}

# Process text with logging
result = await client.call_tool("process_text", {
    "content": "Your text here",
    "analysis_type": "sentiment"
})
# {"status": "completed", "analysis": {...}}
```

### Example 2: Read Resources

```python
# Dynamic resource
welcome = await client.read_resource("greeting://welcome")

# Template resource with format parameter
user_json = await client.read_resource("userinfo://123")  # JSON (default)
user_xml = await client.read_resource("userinfo://123?format=xml")  # XML format
user_text = await client.read_resource("userinfo://123?format=text")  # Plain text

# Wildcard resource
docs = await client.read_resource("docs://getting-started")
```

### Example 3: Use Prompts

```python
# Render prompt
prompt = await client.get_prompt("explain_concept", {
    "concept": "OAuth 2.0",
    "audience_level": "intermediate",
    "include_examples": True
})
```

---

## 🔍 How It Works

### OAuth Flow

1. **Client Registration** - MCP client calls `/register`, gets Google OAuth config
2. **Authorization** - User redirected to Google login
3. **Callback** - Google returns to server callback (`/auth/callback`)
4. **Token Exchange** - Server exchanges code for tokens
5. **Validation** - GoogleProvider validates tokens via Google API

**FastMCP as OAuth Proxy:**

```
Claude Desktop → Your Server (proxy) → Google OAuth
                      ↓
                Token exchange & forward to Claude
```

Only YOUR server's callback URI needed in Google Console!

### Server Architecture

```
Client Request
     ↓
FastMCP Server (main.py)
     ↓
Google OAuth Provider (if --http mode)
     ↓
Tool/Resource/Prompt Execution
     ↓
Response to Client
```

---

## 🛠️ Development

### Adding a New Tool

1. Create `app/tools/my_tool.py`:

```python
async def my_tool(param: str, ctx: Context | None = None) -> dict:
    """Tool description"""
    if ctx:
        await ctx.info("Processing...")
    return {"result": "success"}
```

2. Register in `app/main.py`:

```python
from app.tools.my_tool import my_tool
mcp.tool()(my_tool)
```

3. Add tests in `tests/test_client.py`:

```python
async def test_my_tool():
    async with Client(mcp) as client:
        result = await client.call_tool("my_tool", {"param": "value"})
        assert result.data["result"] == "success"
```

### Adding a New Resource

1. Create `app/resources/my_resource.py`:

```python
def get_my_resource() -> str:
    """Resource content"""
    return "Resource data"
```

2. Register in `app/main.py`:

```python
from app.resources.my_resource import get_my_resource
mcp.resource("myscheme://mypath")(get_my_resource)
```

### Adding a New Prompt

1. Create `app/prompts/my_prompt.py`:

```python
def my_prompt(param: str) -> str:
    """Prompt template"""
    return f"Generate response about {param}..."
```

2. Register in `app/main.py`:

```python
from app.prompts.my_prompt import my_prompt
mcp.prompt()(my_prompt)
```

---

## 🚨 Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause:** Redirect URI not in Google Console

**Solution:** Add `https://your-ngrok-url.ngrok-free.app/auth/callback` to Google Console

### Error: "Module not found"

**Cause:** Dependencies not installed

**Solution:** Run `uv sync`

### Error: "Port already in use"

**Cause:** Another process using port 8000

**Solution:** Kill the process or use different port:

```bash
uv run python -m app.main --http --base-url http://localhost:9000
```

### Tools Hang in Claude Desktop

**Cause:** Some Context operations not fully supported

**Recommendation:** Use these stable tools:

- ✅ `ping`
- ✅ `analyze_text`
- ✅ `process_text`
- ✅ `counter`
- ✅ `get_request_info`
- ✅ `get_forecast`

### ngrok URL Changes

**Issue:** Free ngrok URLs change on restart

**Solution:**

1. Update redirect URI in Google Console
2. Restart server with new URL
3. Update Claude Desktop config

---

## 📖 API Reference

### Tools

#### ping()

Health check endpoint.

**Returns:** `{"status": "ok", "message": "pong", "timestamp": "...", ...}`

#### analyze_text(text: str)

Analyze text statistics.

**Args:**

- `text` - Text to analyze

**Returns:**

```json
{
  "status": "completed",
  "statistics": {
    "characters": 123,
    "letters": 100,
    "digits": 5,
    "spaces": 18,
    "words": 20,
    "sentences": 3,
    "avg_words_per_sentence": 6.7
  },
  "preview": "First 100 characters of text..."
}
```

**Note:** Sentence counting uses simple `.split('.')` and may be inaccurate with abbreviations (e.g., "Dr.", "U.S.A.").

#### process_text(content: str, analysis_type: str = "summary")

Process text with logging and progress tracking.

**Args:**

- `content` - Text content
- `analysis_type` - "summary", "sentiment", or "keywords"

**Returns:**

```json
{
  "status": "completed",
  "features_demonstrated": ["logging", "progress"],
  "content_preview": "First 100 characters...",
  "analysis": {
    "type": "summary|sentiment|keywords",
    "result": "...",
    "characters": 123,
    "words": 20,
    "sentences": 3
  }
}
```

#### counter(action: str = "get")

Session-persistent counter (single-process only).

**Args:**

- `action` - "get", "increment", "decrement", or "reset"

**Returns:** `{"status": "success", "count": 123, "action": "get"}`

**⚠️ Important Limitations:**

- Counter is stored in module-level variable (not truly persistent)
- Resets on server restart
- **Does NOT work with multi-process deployments** (e.g., gunicorn with multiple workers)
- Each process has its own counter value
- For production, use Redis, database, or other shared storage

#### get_request_info()

Get request metadata.

**Returns:** `{"status": "success", "request": {...}, "server": {...}}`

#### get_forecast(city: str = "Jakarta", days: int = 3)

Get weather forecast with randomized mock data.

**Args:**

- `city` - City name (default: "Jakarta")
- `days` - Number of forecast days (1-7, **auto-clamped to valid range if out of bounds**)

**Returns:**

```json
{
  "status": "success",
  "city": "Tokyo",
  "forecast_days": 5,
  "forecast": [
    {
      "date": "2025-10-26",
      "day_name": "Sunday",
      "temperature": { "high": 28, "low": 18, "unit": "°C" },
      "condition": "Sunny",
      "humidity": 65,
      "precipitation_chance": 20
    }
  ],
  "note": "This is mock data. In production, integrate with a real weather API."
}
```

**⚠️ Important Notes:**

- Returns **randomized mock data** - each call produces different values
- `days` parameter is silently clamped to 1-7 range (no error thrown)
- For production use, replace with real weather API (OpenWeatherMap, WeatherAPI, etc.)

### Resources

- `greeting://welcome` - Welcome message
- `userinfo://{user_id}{?format}` - User information (supports `?format=json|xml|text`)
- `docs://{path*}` - Documentation pages (wildcard matching)
- `text://status` - Server operational status
- `text://features` - Feature list
- `file://readme` - README content
- `file://test-results` - Test results (**conditional** - only if TEST_RESULTS.md exists)

### Prompts

#### explain_concept(concept: str, audience_level: str = "intermediate", include_examples: bool = True)

Generate technical explanation.

**Args:**

- `concept` - Concept to explain
- `audience_level` - "beginner", "intermediate", "advanced"
- `include_examples` - Include examples

**Returns:** Formatted prompt string

---

## 🌐 Deployment

### Production Checklist

1. **Set production BASE_URL:**

   ```bash
   BASE_URL=https://your-domain.com
   ```

2. **Update OAuth redirect URI** in Google Console:

   ```
   https://your-domain.com/auth/callback
   ```

3. **Use HTTPS** (required for OAuth)

4. **Set secure environment variables** on hosting platform

5. **Test OAuth flow** before deploying to users

### Hosting Options

- **Railway** - Easy Python deployment
- **Fly.io** - Global edge deployment
- **Heroku** - Classic PaaS
- **VPS** - Full control (DigitalOcean, Linode)

---

## 📜 License

MIT

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 🔗 Links

- **FastMCP Documentation:** https://gofastmcp.com/
- **FastMCP GitHub:** https://github.com/jlowin/fastmcp
- **MCP Specification:** https://modelcontextprotocol.io/
- **Google OAuth 2.0 Guide:** https://developers.google.com/identity/protocols/oauth2

---

**Built with ❤️ using FastMCP**

Questions? Open an issue on GitHub!
