# FastMCP Tool Patterns

This document shows proven tool implementation patterns from production FastMCP servers.

## Tool Pattern Catalog

### 1. Basic Synchronous Tool

**Pattern:** Simple health check or status tool

**Example: ping tool**

```python
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
        return {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
        }
```

**Registration:**

```python
mcp.tool()(ping)
```

**Use When:**

- Health checks
- Simple data retrieval
- No I/O operations needed
- Fast response required

---

### 2. Simple Data Processing Tool

**Pattern:** Synchronous data analysis without external calls

**Example: analyze_text tool**

```python
def analyze_text(text: str) -> dict:
    """
    Analyze text content and return statistics

    Args:
        text: Text to analyze

    Returns:
        dict: Character counts, word count, sentence count, and readability metrics

    Note:
        Sentence counting uses simple .split('.') and may be inaccurate with
        abbreviations (e.g., "Dr.", "U.S.A.").
    """
    # Simple synchronous analysis
    words = text.split()
    sentences = text.split(".")

    # Character type counts
    chars = len(text)
    letters = sum(c.isalpha() for c in text)
    digits = sum(c.isdigit() for c in text)
    spaces = sum(c.isspace() for c in text)

    # Simple readability estimate
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0

    return {
        "status": "completed",
        "statistics": {
            "characters": chars,
            "letters": letters,
            "digits": digits,
            "spaces": spaces,
            "words": len(words),
            "sentences": len(sentences),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        },
        "preview": text[:100] + "..." if len(text) > 100 else text,
    }
```

**Registration:**

```python
mcp.tool()(analyze_text)
```

**Use When:**

- Pure computation (no I/O)
- Data transformation
- Simple analysis
- Fast execution

---

### 3. Tool with Context (Logging & Progress)

**Pattern:** Async tool using Context for logging and progress tracking

**Example: process_text tool**

```python
from fastmcp import Context
import asyncio


async def process_text(
    content: str,
    analysis_type: str = "summary",
    ctx: Context | None = None,
) -> dict:
    """
    Process text with logging and progress tracking

    Args:
        content: Text content to process
        analysis_type: Type of analysis ("summary", "sentiment", "keywords")
        ctx: FastMCP context (auto-injected)

    Returns:
        dict: Analysis results with statistics
    """
    if not ctx:
        # Fallback without context
        return {
            "status": "completed",
            "analysis": basic_analyze(content, analysis_type),
            "note": "Processed without MCP context",
        }

    results = {
        "status": "processing",
        "features_demonstrated": [],
        "content_preview": content[:100] + "..." if len(content) > 100 else content,
    }

    try:
        # Logging
        await ctx.info(f"📄 Processing content ({len(content)} characters)")
        results["features_demonstrated"].append("logging")

        if len(content) < 10:
            await ctx.warning("⚠️  Content is very short")

        await ctx.debug(f"Analysis type: {analysis_type}")

        # Progress tracking
        await ctx.info("📊 Starting analysis...")
        results["features_demonstrated"].append("progress")

        steps = [
            "Tokenizing content",
            "Analyzing structure",
            "Extracting insights",
            "Generating results",
        ]
        total_steps = len(steps)

        for i, step in enumerate(steps):
            await ctx.report_progress(
                progress=i,
                total=total_steps,
                message=f"{step}... ({i + 1}/{total_steps})",
            )
            await ctx.debug(f"Step {i + 1}/{total_steps}: {step}")
            await asyncio.sleep(0.1)  # Simulate processing

        await ctx.report_progress(
            progress=total_steps, total=total_steps, message="Complete!"
        )

        # Perform analysis
        await ctx.info(f"🔍 Performing {analysis_type} analysis...")
        analysis_result = basic_analyze(content, analysis_type)

        results["analysis"] = analysis_result
        results["status"] = "completed"
        await ctx.info("✅ Processing completed successfully!")

    except Exception as e:
        await ctx.error(f"❌ Processing failed: {str(e)}")
        results["status"] = "error"
        results["error"] = str(e)

    return results


def basic_analyze(content: str, analysis_type: str) -> dict:
    """Helper function for actual analysis logic"""
    # ... implementation
    return {"type": analysis_type, "result": "..."}
```

> **Note:** Helper functions in documentation use `# ... implementation` as simplified stubs for clarity. The actual implementation in `reference-project/app/tools/process_text.py` includes comprehensive analysis logic with:
>
> - Text statistics (characters, words, sentences, average lengths)
> - Sentiment analysis with positive/negative indicators
> - Keyword extraction with frequency counts
> - Extractive summarization
>
> See the reference-project for production-ready implementations.

**Registration:**

```python
mcp.tool()(process_text)
```

**Use When:**

- Long-running operations
- Need progress feedback
- Debugging required
- User needs visibility

**Context Features:**

- `await ctx.info()` - Info logging
- `await ctx.debug()` - Debug logging
- `await ctx.warning()` - Warning logging
- `await ctx.error()` - Error logging
- `await ctx.report_progress(progress, total, message)` - Progress updates

---

### 4. Stateful Tool (Module-Level State)

**Pattern:** Tool that maintains state across calls

**Example: counter tool**

```python
from fastmcp import Context

# Module-level counter for demonstration
# ⚠️ In production: use database, Redis, or shared storage
_global_counter = 0


async def counter(action: str = "get", ctx: Context | None = None) -> dict:
    """
    Stateful counter with persistent state

    Args:
        action: Action ("get", "increment", "decrement", "reset")
        ctx: FastMCP context (auto-injected)

    Returns:
        dict: Counter state and action result

    ⚠️ IMPORTANT LIMITATIONS:
    - Counter stored in module-level variable (not truly persistent)
    - Resets to 0 on server restart
    - Does NOT work with multi-process deployments
    - Each process maintains its own separate counter value

    For production use, replace with:
    - Database (PostgreSQL, MySQL)
    - Redis or other distributed cache
    - Any shared storage solution
    """
    global _global_counter

    try:
        if ctx:
            await ctx.info(f"📊 Counter action: {action}")

        if action == "increment":
            _global_counter += 1
            if ctx:
                await ctx.info(f"➕ Incremented to {_global_counter}")

        elif action == "decrement":
            _global_counter -= 1
            if ctx:
                await ctx.info(f"➖ Decremented to {_global_counter}")

        elif action == "reset":
            _global_counter = 0
            if ctx:
                await ctx.warning("🔄 Counter reset to 0")

        elif action == "get":
            if ctx:
                await ctx.debug(f"👁️  Value: {_global_counter}")

        else:
            if ctx:
                await ctx.warning(f"⚠️  Unknown action: {action}")
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "valid_actions": ["get", "increment", "decrement", "reset"],
            }

        return {
            "status": "success",
            "count": _global_counter,
            "action": action,
            "note": "Using module-level variable (not production-ready)",
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"❌ Failed: {str(e)}")
        return {"status": "error", "error": str(e), "action": action}
```

**Registration:**

```python
mcp.tool()(counter)
```

**Use When:**

- State needed across calls
- Session management
- Caching

**⚠️ Production Considerations:**

- Module-level state resets on restart
- Doesn't work with multiple processes
- Use Redis/DB for production

---

### 5. Request Metadata Tool

**Pattern:** Access MCP request information via Context

**Example: get_request_info tool**

```python
from fastmcp import Context


async def get_request_info(ctx: Context | None = None) -> dict:
    """
    Get current request metadata

    Args:
        ctx: FastMCP context (auto-injected)

    Returns:
        dict: Request ID, client ID, session ID, and server info
    """
    if not ctx:
        return {
            "error": "Context not available",
            "note": "This tool requires MCP context to access request metadata",
        }

    try:
        result = {
            "status": "success",
            "request": {
                "request_id": ctx.request_id if hasattr(ctx, "request_id") else None,
                "client_id": ctx.client_id if hasattr(ctx, "client_id") else None,
                "session_id": (
                    ctx.session_id if hasattr(ctx, "session_id") else "N/A (STDIO)"
                ),
            },
            "server": {
                "name": ctx.fastmcp.name if hasattr(ctx, "fastmcp") else "Unknown",
                "transport": "HTTP"
                if hasattr(ctx, "session_id") and ctx.session_id
                else "STDIO",
            },
            "features_demonstrated": ["request_metadata", "context_access"],
        }

        await ctx.info("📋 Request metadata accessed")
        await ctx.debug(f"Request ID: {result['request']['request_id']}")

        return result

    except Exception as e:
        await ctx.error(f"❌ Failed: {str(e)}")
        return {"status": "error", "error": str(e)}
```

**Registration:**

```python
mcp.tool()(get_request_info)
```

**Use When:**

- Debugging
- Audit logging
- Request tracking

---

### 6. External API Integration Tool

**Pattern:** Mock API integration (replace with real API in production)

**Example: get_forecast tool**

```python
import random
from datetime import datetime, timedelta
from fastmcp import Context


async def get_forecast(
    city: str = "Jakarta", days: int = 3, ctx: Context | None = None
) -> dict:
    """
    Get weather forecast for a city

    This tool demonstrates external API integration patterns.
    In production, replace the mock data with actual API calls.

    Args:
        city: City name (default: "Jakarta")
        days: Number of forecast days (1-7, auto-clamped if out of bounds)
        ctx: FastMCP context (optional, for logging)

    Returns:
        Weather forecast data with temperature, conditions, and humidity

    Example:
        get_forecast("Tokyo", 5)
        # Returns 5-day forecast for Tokyo

    Production Usage:
        Replace mock data with real API:
        - OpenWeatherMap: https://openweathermap.org/api
        - WeatherAPI: https://www.weatherapi.com/
        - NOAA: https://www.weather.gov/documentation/services-web-api
    """
    # Validate inputs
    if days < 1 or days > 7:
        days = min(max(days, 1), 7)  # Clamp to 1-7

    if ctx:
        await ctx.info(f"🌤️  Fetching {days}-day forecast for {city}")

    # Mock weather data
    # In production: Replace with actual API call using httpx
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy"]

    forecast_data = []
    base_temp = random.randint(20, 30)

    for day in range(days):
        date = datetime.now() + timedelta(days=day)
        temp_variation = random.randint(-5, 5)

        forecast_data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "temperature": {
                    "high": base_temp + temp_variation + random.randint(0, 3),
                    "low": base_temp + temp_variation - random.randint(3, 8),
                    "unit": "°C",
                },
                "condition": random.choice(conditions),
                "humidity": random.randint(40, 90),
                "precipitation_chance": random.randint(0, 100),
            }
        )

    if ctx:
        await ctx.info("✅ Forecast retrieved successfully")

    return {
        "status": "success",
        "city": city,
        "forecast_days": days,
        "forecast": forecast_data,
        "note": "This is mock data. In production, integrate with a real weather API.",
    }
```

**Registration:**

```python
mcp.tool()(get_forecast)
```

**Use When:**

- Third-party API integration
- External data fetching
- Service composition

**For Production:**
Replace mock data with real API calls:

```python
import httpx

async def get_forecast_production(city: str, days: int, ctx: Context | None = None) -> dict:
    """Production version with real API"""
    api_key = os.getenv("WEATHER_API_KEY")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weatherapi.com/v1/forecast.json",
            params={"key": api_key, "q": city, "days": days},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

    return {
        "status": "success",
        "city": data["location"]["name"],
        "forecast": [
            {
                "date": day["date"],
                "temperature": {
                    "high": day["day"]["maxtemp_c"],
                    "low": day["day"]["mintemp_c"],
                    "unit": "°C",
                },
                "condition": day["day"]["condition"]["text"],
                "humidity": day["day"]["avghumidity"],
            }
            for day in data["forecast"]["forecastday"]
        ],
    }
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
async def my_tool(param: str, ctx: Context | None = None) -> dict:
    try:
        # Tool logic
        result = process(param)
        return {"status": "success", "data": result}
    except ValueError as e:
        if ctx:
            await ctx.warning(f"Invalid input: {e}")
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        if ctx:
            await ctx.error(f"Unexpected error: {e}")
        return {"status": "error", "error": str(e)}
```

### 2. Input Validation

Use type hints and defaults:

```python
def search_users(
    query: str,           # Required
    limit: int = 20,      # Optional with default
    offset: int = 0,      # Optional with default
) -> dict:
    """FastMCP auto-validates based on type hints"""
    # query is guaranteed to be a string
    # limit/offset have defaults
    pass
```

### 3. Clear Documentation

Write comprehensive docstrings:

```python
def my_tool(param: str, limit: int = 10) -> dict:
    """
    One-line summary of what the tool does

    Detailed explanation of the tool's purpose and behavior.
    Explain what it does, when to use it, and any important notes.

    Args:
        param: Description of param (e.g., "search query")
        limit: Description of limit (e.g., "max results, 1-100")

    Returns:
        dict: Description of return value structure:
            {
                "status": str,  # "success" or "error"
                "data": list,   # List of results
                "count": int    # Number of results
            }

    Examples:
        my_tool("example", limit=5) → returns up to 5 results

    Notes:
        - Important caveat 1
        - Important caveat 2
    """
    pass
```

### 4. Async Best Practices

Use `async` for I/O operations:

```python
# ✅ Good: Async for I/O
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Bad: Sync for I/O (blocks)
def fetch_data_sync(url: str) -> dict:
    response = requests.get(url)  # Blocks!
    return response.json()

# ✅ Good: Sync for pure computation
def calculate(x: int, y: int) -> int:
    return x + y  # No I/O, sync is fine
```

### 5. Context Optional Pattern

Always make Context optional:

```python
async def my_tool(param: str, ctx: Context | None = None) -> dict:
    """ctx: Context | None = None allows tool to work without context"""
    if ctx:
        await ctx.info("Processing...")

    # Tool logic works regardless
    result = process(param)

    if ctx:
        await ctx.info("Done!")

    return result
```

## Summary

| Pattern              | Use Case                      | Async? | Context? |
| -------------------- | ----------------------------- | ------ | -------- |
| **Basic Sync**       | Health checks, simple queries | No     | Optional |
| **Data Processing**  | Pure computation              | No     | Optional |
| **With Context**     | Long operations, logging      | Yes    | Required |
| **Stateful**         | State across calls            | Yes    | Optional |
| **Request Metadata** | Debugging, tracking           | Yes    | Required |
| **API Integration**  | External services             | Yes    | Optional |

Choose the pattern that fits your use case!
