"""
Text Analysis Tool

Synchronous text analyzer providing character, word, and sentence statistics.
"""


def analyze_text(text: str) -> dict:
    """
    Analyze text content and return statistics

    Args:
        text: Text to analyze

    Returns:
        dict: Character counts, word count, sentence count, and readability metrics

    Note:
        Sentence counting uses simple .split('.') and may be inaccurate with
        abbreviations (e.g., "Dr.", "U.S.A.") or other edge cases.
    """
    # Simple synchronous analysis
    words = text.split()
    sentences = text.split(".")

    # Character type counts
    chars = len(text)
    letters = sum(c.isalpha() for c in text)
    digits = sum(c.isdigit() for c in text)
    spaces = sum(c.isspace() for c in text)

    # Simple readability estimate (words per sentence)
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
