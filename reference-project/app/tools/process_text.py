"""
Text Processing Tool with Logging and Progress

Advanced text processor demonstrating FastMCP Context features:
- Logging at multiple levels (info, debug, warning, error)
- Real-time progress reporting
- Flexible analysis types (summary, sentiment, keywords)
"""

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
            await ctx.warning("⚠️  Content is very short, analysis may be limited")

        await ctx.debug(f"Analysis type: {analysis_type}")

        # Progress tracking
        await ctx.info("📊 Starting analysis with progress tracking...")
        results["features_demonstrated"].append("progress")

        # Multi-step processing with progress updates
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

        # Report completion
        await ctx.report_progress(
            progress=total_steps, total=total_steps, message="Analysis complete!"
        )

        # Perform basic analysis (without LLM)
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
    """
    Perform basic text analysis without LLM

    Args:
        content: Text to analyze
        analysis_type: Type of analysis

    Returns:
        Analysis results
    """
    words = content.split()
    sentences = [s.strip() for s in content.split(".") if s.strip()]

    basic_stats = {
        "characters": len(content),
        "words": len(words),
        "sentences": len(sentences),
        "avg_word_length": round(sum(len(w) for w in words) / len(words), 1)
        if words
        else 0,
        "avg_words_per_sentence": round(len(words) / len(sentences), 1)
        if sentences
        else 0,
    }

    if analysis_type == "sentiment":
        # Simple sentiment analysis based on common words
        positive_words = [
            "good",
            "great",
            "excellent",
            "happy",
            "love",
            "best",
            "wonderful",
        ]
        negative_words = [
            "bad",
            "terrible",
            "hate",
            "worst",
            "awful",
            "horrible",
            "poor",
        ]

        content_lower = content.lower()
        positive_count = sum(word in content_lower for word in positive_words)
        negative_count = sum(word in content_lower for word in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "type": "sentiment",
            "result": sentiment,
            "details": {
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
            },
            **basic_stats,
        }

    elif analysis_type == "keywords":
        # Extract most common words (excluding common stop words)
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "is",
            "are",
            "was",
            "were",
        }
        word_freq = {}

        for word in words:
            word_clean = word.lower().strip(".,!?;:\"'")
            if word_clean and word_clean not in stop_words and len(word_clean) > 3:
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1

        # Get top 7 keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:7]

        return {
            "type": "keywords",
            "result": [word for word, count in keywords],
            "details": {word: count for word, count in keywords},
            **basic_stats,
        }

    else:  # summary (default)
        # Simple extractive summary - first and last sentences
        summary_sentences = []
        if len(sentences) > 0:
            summary_sentences.append(sentences[0])  # First sentence
        if len(sentences) > 2:
            summary_sentences.append(sentences[-1])  # Last sentence

        return {
            "type": "summary",
            "result": " ".join(summary_sentences)
            if summary_sentences
            else content[:200],
            "note": "Extractive summary (first and last sentences)",
            **basic_stats,
        }
