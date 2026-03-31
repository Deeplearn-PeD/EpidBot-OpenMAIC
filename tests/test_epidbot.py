"""Tests for EpidBot integration."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.adapters.epidbot_adapter import EpidBotAdapter
from src.utils.epidbot_response_parser import EpidBotResponseParser


class TestEpidBotResponseParser:
    """Tests for the EpidBotResponseParser class."""

    def test_parse_table_success(self):
        markdown = """
| Metric | Value |
|--------|-------|
| total_cases | 1234 |
| deaths | 5 |
| hospitalizations | 42 |
| fatality_rate | 0.41 |
"""
        result = EpidBotResponseParser.parse_dengue_summary(markdown)
        assert result is not None
        assert result["total_cases"] == 1234
        assert result["deaths"] == 5
        assert result["hospitalizations"] == 42
        assert result["fatality_rate"] == 0.41

    def test_parse_bold_patterns(self):
        markdown = """
**Total Cases:** 5000
**Deaths:** 25
**Hospitalizations:** 150
**Fatality Rate:** 0.5
"""
        result = EpidBotResponseParser.parse_dengue_summary(markdown)
        assert result is not None
        assert result["total_cases"] == 5000
        assert result["deaths"] == 25
        assert result["hospitalizations"] == 150
        assert result["fatality_rate"] == 0.5

    def test_parse_list_patterns(self):
        markdown = """
- Total cases: 3000
- Deaths: 10
- Hospitalizations: 100
- Fatality rate: 0.33
"""
        result = EpidBotResponseParser.parse_dengue_summary(markdown)
        assert result is not None
        assert result["total_cases"] == 3000
        assert result["deaths"] == 10
        assert result["hospitalizations"] == 100
        assert result["fatality_rate"] == 0.33

    def test_parse_incomplete_data_returns_none(self):
        markdown = """
| Metric | Value |
|--------|-------|
| total_cases | 1000 |
"""
        result = EpidBotResponseParser.parse_dengue_summary(markdown)
        assert result is None

    def test_parse_empty_string_returns_none(self):
        result = EpidBotResponseParser.parse_dengue_summary("")
        assert result is None

    def test_parse_none_returns_none(self):
        result = EpidBotResponseParser.parse_dengue_summary(None)
        assert result is None


class TestEpidBotAdapter:
    """Tests for the EpidBotAdapter class."""

    @pytest.fixture
    def adapter(self):
        return EpidBotAdapter(base_url="https://api.epidbot.kwar-ai.com.br", api_key="test-key-123")

    def test_init(self, adapter):
        assert adapter.base_url == "https://api.epidbot.kwar-ai.com.br"
        assert adapter.api_key == "test-key-123"
        assert adapter._session_id is None

    def test_get_headers(self, adapter):
        headers = adapter._get_headers()
        assert headers["X-API-Key"] == "test-key-123"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_create_session(self, adapter):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 42, "name": "openmaic-bridge"}
        mock_response.raise_for_status = MagicMock()

        with patch.object(adapter, "_get_headers") as mock_headers:
            mock_headers.return_value = {"X-API-Key": "test-key-123"}
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                session_id = await adapter.create_session()
                assert session_id == 42
                assert adapter._session_id == 42

    @pytest.mark.asyncio
    async def test_chat_without_session_raises(self, adapter):
        with pytest.raises(RuntimeError, match="Session not created"):
            await adapter.chat("test message")

    @pytest.mark.asyncio
    async def test_health_check_success(self, adapter):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await adapter.health_check()
            assert result is True
