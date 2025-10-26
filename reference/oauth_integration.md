# OAuth Integration with FastMCP

FastMCP has built-in support for Google OAuth 2.0, making it easy to add authentication to your MCP server for remote access.

## Why OAuth?

**OAuth is required for:**

- Remote access via HTTP/HTTPS
- Multi-user servers
- Production deployments
- Secure token-based authentication

**OAuth is NOT needed for:**

- Local development (STDIO mode)
- Single-user local testing
- Development without network access

## Google OAuth Setup

### Step 1: Create OAuth Client in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing
3. Navigate to **"APIs & Services" → "Credentials"**
4. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
5. Configure:
   - **Application type**: Web application
   - **Name**: Your server name (e.g., "My MCP Server")
   - **Authorized redirect URIs**: Add your server's callback URL

**⚠️ IMPORTANT:**
Only add **YOUR server's callback URI**, not Claude Desktop's callback.
FastMCP acts as an OAuth proxy.

**Example redirect URI:**

```
https://your-ngrok-url.ngrok-free.app/auth/callback
```

6. Save and copy:
   - Client ID
   - Client Secret

### Step 2: Configure Environment Variables

Create `.env` file:

```bash
# Google OAuth credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Server base URL
BASE_URL=http://localhost:8000
```

**For production:**

```bash
BASE_URL=https://your-domain.com
# or for ngrok:
BASE_URL=https://abc123.ngrok-free.app
```

### Step 3: Implement GoogleProvider

**In `app/config.py`:**

```python
import os
from dotenv import load_dotenv

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
    SERVER_NAME = "My MCP Server"
    SERVER_VERSION = "1.0.0"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.GOOGLE_CLIENT_ID or not cls.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Missing required environment variables. "
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file"
            )

# Validate on import
Config.validate()
```

**In `app/main.py`:**

```python
import argparse
from urllib.parse import urlparse
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

from app.config import Config
from app.common import register_all

# Parse command-line arguments
parser = argparse.ArgumentParser(description="My MCP Server")
parser.add_argument(
    "--http", action="store_true", help="Run in HTTP mode (default: stdio)"
)
parser.add_argument(
    "--base-url",
    type=str,
    default=Config.BASE_URL,
    help="Override base URL (e.g., https://your-ngrok-url.ngrok-free.app)",
)
args, unknown = parser.parse_known_args()

# Setup Google OAuth Provider
auth = GoogleProvider(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    base_url=args.base_url,
    required_scopes=Config.REQUIRED_SCOPES,
    redirect_path=Config.REDIRECT_PATH,
)

# Create FastMCP server with authentication
mcp = FastMCP(
    name=Config.SERVER_NAME,
    auth=auth,
)

# Register all tools, resources, and prompts
register_all(mcp)

def run_server():
    """Run the MCP server"""
    if args.http:
        # HTTP mode for remote access
        print("🚀 Starting MCP server in HTTP mode")
        print(f"📍 Base URL: {args.base_url}")
        print(f"📡 MCP endpoint: {args.base_url}/mcp/")
        print(f"🔐 OAuth metadata: {args.base_url}/.well-known/oauth-authorization-server")
        print()

        # Extract port from base URL (default: 8000)
        parsed = urlparse(args.base_url)
        port = parsed.port or 8000

        # Always bind to 0.0.0.0 for ngrok compatibility
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        # STDIO mode (default)
        mcp.run()

if __name__ == "__main__":
    run_server()
```

## OAuth Flow

### How It Works

```
1. Client Registration
   Claude Desktop → Your Server (/register)
   ← Google OAuth config

2. Authorization
   Claude Desktop → Google login page
   User authorizes → Google

3. Callback
   Google → Your Server (/auth/callback)
   Your Server exchanges code for tokens

4. Token Validation
   Your Server → Google API (validate token)
   ← User info

5. Access Granted
   Your Server → Claude Desktop
   ← Authenticated session
```

**FastMCP as OAuth Proxy:**

```
Claude Desktop → Your MCP Server (proxy) → Google OAuth
                       ↓
                 Token exchange & forward to Claude
```

Only **YOUR server's callback URI** is needed in Google Console!

## Deployment

### Local Testing with ngrok

**Terminal 1: Start ngrok**

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Terminal 2: Start server**

```bash
# Update BASE_URL in .env or use --base-url flag
uv run python -m app.main --http --base-url https://abc123.ngrok-free.app
```

**Terminal 3: Update Google Console**

1. Go to Google Cloud Console
2. Add redirect URI: `https://abc123.ngrok-free.app/auth/callback`
3. Save

### Configure Claude Desktop

**⚠️ IMPORTANT:** Remote HTTP servers with OAuth **CANNOT** be configured via `claude_desktop_config.json`. You **MUST** use the Connectors UI.

**Requirements:**

- Claude Desktop with Connectors support
- Claude Pro, Max, Team, or Enterprise plan
- Running server with ngrok (or production URL)

**Steps:**

1. Open Claude Desktop
2. Go to **Settings > Connectors**
3. Click **"Add custom connector"**
4. Enter your server URL: `https://abc123.ngrok-free.app`
5. Claude will handle OAuth authentication automatically

### Production Deployment

**For production (Railway, Fly.io, VPS, etc.):**

1. **Set production BASE_URL:**

   ```bash
   BASE_URL=https://your-domain.com
   ```

2. **Update OAuth redirect URI in Google Console:**

   ```
   https://your-domain.com/auth/callback
   ```

3. **Use HTTPS** (required for OAuth)

4. **Set secure environment variables** on hosting platform

5. **Test OAuth flow** before deploying to users

## Dual-Mode Pattern: With and Without OAuth

Maintain both authenticated and non-authenticated versions:

**app/main.py (with OAuth):**

```python
from fastmcp.server.auth.providers.google import GoogleProvider

auth = GoogleProvider(...)
mcp = FastMCP(name="My Server", auth=auth)
register_all(mcp)
```

**app/main_noauth.py (without OAuth):**

```python
mcp = FastMCP(name="My Server (No Auth)")  # No auth parameter
register_all(mcp)
```

**Benefits:**

- ✅ Local development without OAuth setup
- ✅ Faster testing (no network calls)
- ✅ CI/CD friendly (no credentials needed)
- ✅ Easy debugging in STDIO mode
- ✅ Production uses OAuth

**Usage:**

```bash
# Local development (no auth)
uv run python -m app.main_noauth

# Production (with OAuth)
uv run python -m app.main --http --base-url https://your-server.com
```

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause:** Redirect URI not in Google Console or doesn't match exactly

**Solution:**

1. Check redirect URI in Google Console
2. Ensure it matches: `{BASE_URL}/auth/callback`
3. For ngrok: Update every time ngrok URL changes
4. No trailing slash in BASE_URL

### Error: "Invalid client"

**Cause:** Wrong Client ID or Client Secret

**Solution:**

1. Verify `GOOGLE_CLIENT_ID` in `.env`
2. Verify `GOOGLE_CLIENT_SECRET` in `.env`
3. Check for typos or extra spaces
4. Regenerate credentials if needed

### Error: "Access denied"

**Cause:** User didn't grant required scopes

**Solution:**

1. Check `REQUIRED_SCOPES` in config
2. Ensure user grants all required permissions
3. Try clearing browser cookies and retry

### ngrok URL Changes

**Issue:** Free ngrok URLs change on restart

**Solution:**

1. Update redirect URI in Google Console with new ngrok URL
2. Restart server with new `--base-url`
3. Reconnect Claude Desktop

**Or use ngrok paid plan for static domains**

### Server Not Accessible

**Cause:** Firewall, wrong port, or host binding

**Solution:**

1. Bind to `0.0.0.0`, not `localhost` or `127.0.0.1`
2. Check firewall allows port 8000
3. Verify ngrok is running and forwarding
4. Test: `curl https://your-ngrok-url.ngrok-free.app/`

## Security Best Practices

### 1. Environment Variables

**✅ Good:**

```python
# Use environment variables
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
```

**❌ Bad:**

```python
# Hardcoded secrets
GOOGLE_CLIENT_SECRET = "abc123secret"  # NEVER DO THIS
```

### 2. .gitignore

Always ignore `.env`:

```gitignore
.env
.env.local
.env.production
```

### 3. Scope Principle

Only request scopes you actually need:

```python
# ✅ Good: Minimal scopes
REQUIRED_SCOPES = [
    "openid",
    "email",
    "profile",
]

# ❌ Bad: Unnecessary scopes
REQUIRED_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/drive",  # Don't need this!
    "https://www.googleapis.com/auth/calendar",  # Don't need this!
]
```

### 4. HTTPS in Production

Always use HTTPS for OAuth in production:

```python
# ✅ Good
BASE_URL = "https://your-domain.com"

# ❌ Bad (OAuth won't work properly)
BASE_URL = "http://your-domain.com"
```

## OAuth vs No-Auth Decision Tree

```
Do you need remote access?
├─ Yes
│  └─ Use OAuth (main.py)
│     - HTTP transport
│     - GoogleProvider
│     - Production ready
│
└─ No (local only)
   └─ No auth needed (main_noauth.py)
      - STDIO transport
      - Faster development
      - No credentials required
```

## Summary

| Aspect             | With OAuth             | Without OAuth                |
| ------------------ | ---------------------- | ---------------------------- |
| **File**           | `main.py`              | `main_noauth.py`             |
| **Transport**      | HTTP/HTTPS             | STDIO                        |
| **Access**         | Remote                 | Local only                   |
| **Setup**          | Google OAuth required  | None                         |
| **Use Case**       | Production, multi-user | Development, testing         |
| **Claude Desktop** | Connectors UI          | `claude_desktop_config.json` |

For most production deployments, use OAuth. For local development, use no-auth version for faster iteration.
