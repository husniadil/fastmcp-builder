"""
Unit tests for tools
"""

import pytest
from app.tools.ping import ping
from app.tools.analyze_text import analyze_text
from app.tools.process_text import process_text
from app.tools.counter import counter
from app.tools.request_info import get_request_info
from app.tools.get_forecast import get_forecast


class TestPingTool:
    """Tests for basic ping tool"""

    def test_ping_returns_dict(self):
        """ping() should return a dictionary"""
        result = ping()
        assert isinstance(result, dict)

    def test_ping_has_required_fields(self):
        """ping() should have all required fields"""
        result = ping()

        assert "status" in result
        assert "message" in result
        assert "timestamp" in result
        assert "response_time_ms" in result
        assert "server" in result

    def test_ping_status_ok(self):
        """ping() should return status 'ok'"""
        result = ping()
        assert result["status"] == "ok"

    def test_ping_message_pong(self):
        """ping() should return message 'pong'"""
        result = ping()
        assert result["message"] == "pong"

    def test_ping_has_response_time(self):
        """ping() should measure response time"""
        result = ping()
        assert isinstance(result["response_time_ms"], (int, float))
        assert result["response_time_ms"] >= 0

    def test_ping_has_server_info(self):
        """ping() should include server metadata"""
        result = ping()
        server = result["server"]

        assert "name" in server
        assert "version" in server
        assert "base_url" in server


class TestAnalyzeTextTool:
    """Tests for analyze_text tool"""

    def test_analyze_text_returns_dict(self):
        """analyze_text() should return a dictionary"""
        result = analyze_text("Hello world")
        assert isinstance(result, dict)

    def test_analyze_text_has_required_fields(self):
        """analyze_text() should have status and statistics"""
        result = analyze_text("Test text")

        assert "status" in result
        assert "statistics" in result
        assert result["status"] == "completed"

    def test_analyze_text_counts_characters(self):
        """analyze_text() should count characters correctly"""
        result = analyze_text("Hello")
        stats = result["statistics"]

        assert stats["characters"] == 5
        assert stats["letters"] == 5

    def test_analyze_text_counts_characters_with_spaces(self):
        """analyze_text() should count characters with spaces"""
        result = analyze_text("Hello world")
        stats = result["statistics"]

        assert stats["characters"] == 11
        assert stats["letters"] == 10  # Only letters, no spaces
        assert stats["spaces"] == 1

    def test_analyze_text_counts_words(self):
        """analyze_text() should count words correctly"""
        result = analyze_text("One two three")
        stats = result["statistics"]

        assert stats["words"] == 3

    def test_analyze_text_counts_sentences(self):
        """analyze_text() should count sentences correctly"""
        result = analyze_text("First sentence. Second sentence. Third!")
        stats = result["statistics"]

        assert stats["sentences"] == 3

    def test_analyze_text_empty_string(self):
        """analyze_text() should handle empty string"""
        result = analyze_text("")
        stats = result["statistics"]

        assert stats["characters"] == 0
        assert stats["words"] == 0

    def test_analyze_text_has_avg_words_per_sentence(self):
        """analyze_text() should calculate average words per sentence"""
        result = analyze_text("Hello world. This is a test.")
        stats = result["statistics"]

        assert "avg_words_per_sentence" in stats
        assert isinstance(stats["avg_words_per_sentence"], (int, float))


class TestProcessTextTool:
    """Tests for process_text tool"""

    @pytest.mark.asyncio
    async def test_process_text_returns_dict(self):
        """process_text() should return a dictionary"""
        result = await process_text("Test content")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_process_text_has_required_fields(self):
        """process_text() should have status and analysis"""
        result = await process_text("Test content")

        assert "status" in result
        assert "analysis" in result
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_process_text_summary_analysis(self):
        """process_text() should handle summary analysis"""
        result = await process_text("Test content", analysis_type="summary")

        assert result["analysis"]["type"] == "summary"
        assert "result" in result["analysis"]

    @pytest.mark.asyncio
    async def test_process_text_sentiment_analysis(self):
        """process_text() should handle sentiment analysis"""
        result = await process_text("Great content!", analysis_type="sentiment")

        assert result["analysis"]["type"] == "sentiment"
        assert "result" in result["analysis"]

    @pytest.mark.asyncio
    async def test_process_text_keywords_analysis(self):
        """process_text() should handle keywords analysis"""
        result = await process_text("Python FastMCP MCP", analysis_type="keywords")

        assert result["analysis"]["type"] == "keywords"
        assert "result" in result["analysis"]

    @pytest.mark.asyncio
    async def test_process_text_with_context(self, mock_context):
        """process_text() should log when context available"""
        await process_text("Test", ctx=mock_context)

        # Should call info logging
        assert mock_context.info.call_count > 0

    @pytest.mark.asyncio
    async def test_process_text_without_context(self):
        """process_text() should work without context"""
        result = await process_text("Test", ctx=None)

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_process_text_features_demonstrated(self):
        """process_text() should demonstrate FastMCP features"""
        result = await process_text("Test", ctx=None)

        # Without context, no features demonstrated
        assert result["status"] == "completed"
        assert "analysis" in result


class TestCounterTool:
    """Tests for counter tool"""

    @pytest.mark.asyncio
    async def test_counter_returns_dict(self):
        """counter() should return a dictionary"""
        result = await counter("get")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_counter_get_action(self):
        """counter() should get current count"""
        await counter("reset")  # Reset first
        result = await counter("get")

        assert result["status"] == "success"
        assert result["action"] == "get"
        assert "count" in result

    @pytest.mark.asyncio
    async def test_counter_increment_action(self):
        """counter() should increment count"""
        await counter("reset")
        result = await counter("increment")

        assert result["status"] == "success"
        assert result["action"] == "increment"
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_counter_decrement_action(self):
        """counter() should decrement count"""
        await counter("reset")
        await counter("increment")
        await counter("increment")
        result = await counter("decrement")

        assert result["status"] == "success"
        assert result["action"] == "decrement"
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_counter_reset_action(self):
        """counter() should reset count to 0"""
        await counter("increment")
        await counter("increment")
        result = await counter("reset")

        assert result["status"] == "success"
        assert result["action"] == "reset"
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_counter_invalid_action(self):
        """counter() should handle invalid action"""
        result = await counter("invalid_action")

        assert result["status"] == "error"
        assert "error" in result
        assert "valid_actions" in result

    @pytest.mark.asyncio
    async def test_counter_default_action_is_get(self):
        """counter() should default to 'get' action"""
        await counter("reset")
        result = await counter()

        assert result["action"] == "get"

    @pytest.mark.asyncio
    async def test_counter_with_context(self, mock_context):
        """counter() should log when context available"""
        await counter("get", ctx=mock_context)

        # Should call info logging
        assert mock_context.info.call_count > 0

    @pytest.mark.asyncio
    async def test_counter_features_demonstrated(self):
        """counter() should demonstrate state management"""
        result = await counter("get")

        assert "features_demonstrated" in result
        features = result["features_demonstrated"]
        assert "persistent_state" in features


class TestRequestInfoTool:
    """Tests for get_request_info tool"""

    @pytest.mark.asyncio
    async def test_request_info_returns_dict(self):
        """get_request_info() should return a dictionary"""
        result = await get_request_info()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_request_info_without_context(self):
        """get_request_info() should handle missing context"""
        result = await get_request_info(ctx=None)

        assert "error" in result
        assert "Context not available" in result["error"]

    @pytest.mark.asyncio
    async def test_request_info_with_context(self, mock_context):
        """get_request_info() should extract request metadata"""
        mock_context.request_id = "test-request-123"
        mock_context.client_id = "test-client-456"
        mock_context.session_id = "test-session-789"
        mock_context.fastmcp.name = "Test Server"

        result = await get_request_info(ctx=mock_context)

        assert result["status"] == "success"
        assert "request" in result
        assert "server" in result

    @pytest.mark.asyncio
    async def test_request_info_has_request_metadata(self, mock_context):
        """get_request_info() should include request metadata"""
        mock_context.request_id = "test-123"
        mock_context.client_id = "client-456"

        result = await get_request_info(ctx=mock_context)

        request = result["request"]
        assert "request_id" in request
        assert "client_id" in request
        assert "session_id" in request

    @pytest.mark.asyncio
    async def test_request_info_has_server_info(self, mock_context):
        """get_request_info() should include server info"""
        result = await get_request_info(ctx=mock_context)

        server = result["server"]
        assert "name" in server
        assert "transport" in server

    @pytest.mark.asyncio
    async def test_request_info_logs_access(self, mock_context):
        """get_request_info() should log access"""
        await get_request_info(ctx=mock_context)

        # Should call info and debug logging
        assert mock_context.info.call_count > 0
        assert mock_context.debug.call_count > 0

    @pytest.mark.asyncio
    async def test_request_info_features_demonstrated(self, mock_context):
        """get_request_info() should demonstrate context features"""
        result = await get_request_info(ctx=mock_context)

        assert "features_demonstrated" in result
        features = result["features_demonstrated"]
        assert "request_metadata" in features
        assert "context_access" in features


class TestGetForecastTool:
    """Tests for get_forecast tool"""

    @pytest.mark.asyncio
    async def test_get_forecast_returns_dict(self):
        """get_forecast() should return a dictionary"""
        result = await get_forecast()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_forecast_has_required_fields(self):
        """get_forecast() should have status and forecast"""
        result = await get_forecast()

        assert result["status"] == "success"
        assert "city" in result
        assert "forecast" in result
        assert "forecast_days" in result

    @pytest.mark.asyncio
    async def test_get_forecast_default_city(self):
        """get_forecast() should default to Jakarta"""
        result = await get_forecast()

        assert result["city"] == "Jakarta"

    @pytest.mark.asyncio
    async def test_get_forecast_custom_city(self):
        """get_forecast() should use provided city"""
        result = await get_forecast(city="Tokyo")

        assert result["city"] == "Tokyo"

    @pytest.mark.asyncio
    async def test_get_forecast_default_days(self):
        """get_forecast() should default to 3 days"""
        result = await get_forecast()

        assert result["forecast_days"] == 3
        assert len(result["forecast"]) == 3

    @pytest.mark.asyncio
    async def test_get_forecast_custom_days(self):
        """get_forecast() should use provided days"""
        result = await get_forecast(days=5)

        assert result["forecast_days"] == 5
        assert len(result["forecast"]) == 5

    @pytest.mark.asyncio
    async def test_get_forecast_validates_days_min(self):
        """get_forecast() should enforce minimum days"""
        result = await get_forecast(days=0)

        # Should be clamped to 1
        assert len(result["forecast"]) >= 1

    @pytest.mark.asyncio
    async def test_get_forecast_validates_days_max(self):
        """get_forecast() should enforce maximum days"""
        result = await get_forecast(days=10)

        # Should be clamped to 7
        assert len(result["forecast"]) <= 7

    @pytest.mark.asyncio
    async def test_get_forecast_data_structure(self):
        """get_forecast() should return properly structured data"""
        result = await get_forecast(days=2)

        forecast = result["forecast"]
        assert len(forecast) == 2

        # Check first day structure
        day = forecast[0]
        assert "date" in day
        assert "day_name" in day
        assert "temperature" in day
        assert "condition" in day
        assert "humidity" in day
        assert "precipitation_chance" in day

    @pytest.mark.asyncio
    async def test_get_forecast_temperature_structure(self):
        """get_forecast() should have proper temperature structure"""
        result = await get_forecast()

        temp = result["forecast"][0]["temperature"]
        assert "high" in temp
        assert "low" in temp
        assert "unit" in temp
        assert temp["unit"] == "°C"

    @pytest.mark.asyncio
    async def test_get_forecast_with_context(self, mock_context):
        """get_forecast() should log when context available"""
        await get_forecast(ctx=mock_context)

        # Should call info logging
        assert mock_context.info.call_count > 0

    @pytest.mark.asyncio
    async def test_get_forecast_without_context(self):
        """get_forecast() should work without context"""
        result = await get_forecast(ctx=None)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_forecast_has_note(self):
        """get_forecast() should include note about mock data"""
        result = await get_forecast()

        assert "note" in result
        assert "mock" in result["note"].lower()
