"""
Prompt Example: Explain Concept

A universal prompt for explaining technical concepts with customizable
audience level and optional examples.

Prompts are reusable message templates that clients can use to
generate consistent, well-structured requests to LLMs.
"""


def explain_concept(
    concept: str,
    audience_level: str = "intermediate",
    include_examples: bool = True,
) -> str:
    """
    Generate a prompt to explain a technical concept

    This is a prompt template that demonstrates:
    - Multiple parameters for customization
    - Conditional content based on parameters
    - Audience-appropriate language
    - Flexible structure for different use cases

    Args:
        concept: The concept to explain (e.g., "OAuth 2.0", "MCP", "FastMCP")
        audience_level: Target audience skill level
            - "beginner": Simple language, avoid jargon
            - "intermediate": Technical but clear explanations (default)
            - "advanced": Deep technical details and considerations
        include_examples: Whether to request practical examples (default: True)

    Returns:
        Formatted prompt string ready for LLM

    Examples:
        explain_concept("OAuth 2.0", "beginner", True)
        → Prompt asking for beginner-friendly OAuth explanation with examples

        explain_concept("FastMCP Context", "advanced", False)
        → Prompt asking for advanced FastMCP Context explanation without examples

    Usage in MCP Client:
        1. Client lists available prompts
        2. User selects "explain_concept"
        3. Client prompts user for arguments
        4. Prompt is generated and sent to LLM
        5. LLM returns explanation
    """

    prompt = f"Please explain the concept of '{concept}' "
    prompt += f"for a {audience_level} audience.\n\n"

    # Customize language based on audience level
    if audience_level == "beginner":
        prompt += (
            "Use simple, clear language and avoid technical jargon when possible. "
        )
        prompt += "Explain terms that must be used. "
        prompt += (
            "Focus on high-level understanding rather than implementation details.\n"
        )

    elif audience_level == "advanced":
        prompt += "Include technical details, implementation considerations, and advanced use cases. "
        prompt += "Discuss edge cases, performance implications, and best practices. "
        prompt += "Assume familiarity with related concepts.\n"

    else:  # intermediate (default)
        prompt += "Use technical terminology but explain it clearly. "
        prompt += "Balance conceptual understanding with practical details. "
        prompt += "Assume basic technical knowledge.\n"

    # Add example request if enabled
    if include_examples:
        prompt += "\nPlease include:\n"
        prompt += "1. A clear definition\n"
        prompt += "2. Key components or concepts\n"
        prompt += "3. Practical examples or use cases\n"
        prompt += "4. Common pitfalls or misconceptions (if applicable)\n"

    else:
        prompt += "\nProvide a clear definition and explanation of key aspects.\n"

    return prompt
