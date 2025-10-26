"""
Pytest configuration and shared fixtures
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass


@dataclass
class MockRoot:
    """Mock root for testing"""

    uri: str


@dataclass
class MockLLMResponse:
    """Mock LLM response"""

    text: str


@dataclass
class MockElicitResult:
    """Mock elicitation result"""

    action: str  # "accept", "decline", "cancel"
    data: object = None


@pytest.fixture
def mock_context():
    """
    Mock FastMCP Context for testing

    Provides mocked versions of all Context methods:
    - list_roots()
    - debug(), info(), warning(), error()
    - elicit()
    - report_progress()
    - sample()
    """
    ctx = AsyncMock()

    # Mock roots
    ctx.list_roots = AsyncMock(
        return_value=[
            MockRoot(uri="file:///home/user/documents"),
            MockRoot(uri="file:///home/user/projects"),
        ]
    )

    # Mock logging methods (no return value)
    ctx.debug = AsyncMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()

    # Mock elicitation (default: accept)
    ctx.elicit = AsyncMock(
        return_value=MockElicitResult(
            action="accept",
            data=MagicMock(analysis_type="summary", max_length=100),
        )
    )

    # Mock progress reporting
    ctx.report_progress = AsyncMock()

    # Mock LLM sampling
    ctx.sample = AsyncMock(
        return_value=MockLLMResponse(
            text="This is a comprehensive analysis of the provided content."
        )
    )

    return ctx


@pytest.fixture
def sample_content():
    """Sample text content for testing"""
    return """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
    """


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
