"""
Unit tests for prompts
"""

from app.prompts.explain import explain_concept


class TestExplainConceptPrompt:
    """Tests for explain_concept prompt"""

    def test_explain_concept_returns_string(self):
        """explain_concept() should return a string"""
        result = explain_concept("OAuth 2.0")
        assert isinstance(result, str)

    def test_explain_concept_includes_concept(self):
        """explain_concept() should mention the concept"""
        result = explain_concept("FastMCP")
        assert "FastMCP" in result

    def test_explain_concept_default_audience_is_intermediate(self):
        """explain_concept() should use intermediate audience by default"""
        result = explain_concept("MCP")
        assert "intermediate" in result

    def test_explain_concept_beginner_audience(self):
        """explain_concept() for beginner should use simple language"""
        result = explain_concept("API", audience_level="beginner")

        # Should mention beginner
        assert "beginner" in result

        # Should request simple language
        assert "simple" in result.lower() or "jargon" in result.lower()

    def test_explain_concept_advanced_audience(self):
        """explain_concept() for advanced should include technical details"""
        result = explain_concept("Protocol", audience_level="advanced")

        # Should mention advanced
        assert "advanced" in result

        # Should request technical details
        assert "technical" in result.lower() or "implementation" in result.lower()

    def test_explain_concept_with_examples(self):
        """explain_concept() with include_examples=True should request examples"""
        result = explain_concept("REST API", include_examples=True)

        # Should request examples
        assert "example" in result.lower()

    def test_explain_concept_without_examples(self):
        """explain_concept() with include_examples=False should not request examples"""
        result = explain_concept("GraphQL", include_examples=False)

        # Should not mention examples
        assert "example" not in result.lower()

    def test_explain_concept_custom_combination(self):
        """explain_concept() should support custom audience and examples combination"""
        result = explain_concept(
            "Microservices", audience_level="advanced", include_examples=False
        )

        # Should be for advanced audience
        assert "advanced" in result

        # Should not request examples
        assert "example" not in result.lower()

    def test_explain_concept_not_empty(self):
        """explain_concept() should not return empty string"""
        result = explain_concept("Test")
        assert len(result) > 0

    def test_explain_concept_is_well_formed(self):
        """explain_concept() should be a well-formed prompt"""
        result = explain_concept("Authentication")

        # Should be a proper question/request
        assert "explain" in result.lower() or "please" in result.lower()

        # Should end with useful instructions
        assert len(result.split("\n")) > 1  # Multiple lines/sections
