"""
Static Resources - Class-Based Resources

Demonstrates FastMCP's static resource types:
- TextResource: Static text content
- FileResource: Expose local files

These are registered differently from function-based resources.
"""

from pathlib import Path
from fastmcp.resources import TextResource, FileResource


# Text Resource - Static text content
status_resource = TextResource(
    uri="text://status",
    text="🟢 MCP Auth Demo Server is operational\n\nAll systems running normally.",
    name="Server Status",
    description="Current server operational status",
    mime_type="text/plain",
)

# Another text resource with structured data
features_resource = TextResource(
    uri="text://features",
    text="""# MCP Auth Demo Features

✅ **Working in Claude Desktop:**
- OAuth Authentication (Google)
- Basic Tools (ping, analyze_text, process_text)
- Static & Dynamic Resources
- Universal Prompts
- Logging & Progress

⚠️ **Limited Support:**
- Roots (hangs)
- Elicitation (not found)
- Sampling (hangs)

📚 See README.md for complete documentation.
""",
    name="Feature List",
    description="List of implemented features",
    mime_type="text/markdown",
)

# File Resource - Expose README
readme_resource = FileResource(
    uri="file://readme",
    path=Path(__file__).parent.parent.parent / "README.md",
    name="Project README",
    description="Complete project documentation",
    mime_type="text/markdown",
)

# File Resource - Expose test results
try:
    test_results_path = Path(__file__).parent.parent.parent / "TEST_RESULTS.md"
    if test_results_path.exists():
        test_results_resource = FileResource(
            uri="file://test-results",
            path=test_results_path,
            name="Test Results",
            description="Complete test results and compatibility matrix",
            mime_type="text/markdown",
        )
    else:
        test_results_resource = None
except Exception:
    test_results_resource = None


# Export all static resources
def get_static_resources():
    """
    Get all static resources for registration

    Returns:
        List of static resource instances
    """
    resources = [
        status_resource,
        features_resource,
        readme_resource,
    ]

    if test_results_resource:
        resources.append(test_results_resource)

    return resources
