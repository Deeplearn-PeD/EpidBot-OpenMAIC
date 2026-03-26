"""Basic tests for EpidBot-OpenMAIC Bridge."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.generators.requirement_builder import RequirementBuilder
from src.utils.data_fetcher import DengueDataFetcher


class TestRequirementBuilder:
    """Tests for the RequirementBuilder class."""

    def test_build_dengue_training_basic(self):
        builder = RequirementBuilder()
        data_summary = {
            "total_cases": 1000,
            "deaths": 5,
            "hospitalizations": 50,
            "fatality_rate": 0.5,
            "by_week": {1: 100, 2: 150, 3: 200},
        }

        result = builder.build_dengue_training(
            data_summary=data_summary,
            region="São Paulo",
            timeframe="Ano 2024",
        )

        assert "São Paulo" in result
        assert "1,000" in result
        assert "5" in result
        assert "agentes de saúde" in result
        assert "Semana Epidemiológica" in result

    def test_build_dengue_training_empty_data(self):
        builder = RequirementBuilder()
        data_summary = {
            "total_cases": 0,
            "deaths": 0,
            "hospitalizations": 0,
            "fatality_rate": 0.0,
            "by_week": {},
        }

        result = builder.build_dengue_training(
            data_summary=data_summary,
            region="Test Region",
            timeframe="Test Period",
        )

        assert "Test Region" in result
        assert "0" in result

    def test_format_weekly_data(self):
        builder = RequirementBuilder()

        weekly = {1: 10, 2: 20, 3: 30}
        result = builder._format_weekly_data(weekly)

        assert "Semana Epidemiológica" in result
        assert "| 1 | 10 |" in result
        assert "| 2 | 20 |" in result
        assert "| 3 | 30 |" in result

    def test_format_weekly_data_empty(self):
        builder = RequirementBuilder()
        result = builder._format_weekly_data({})
        assert "não disponíveis" in result


class TestDengueDataFetcher:
    """Tests for the DengueDataFetcher class."""

    def test_summarize_empty_dataframe(self):
        import pandas as pd

        fetcher = DengueDataFetcher()
        df = pd.DataFrame()
        result = fetcher.summarize(df)

        assert result["total_cases"] == 0
        assert result["deaths"] == 0
        assert result["hospitalizations"] == 0
        assert result["fatality_rate"] == 0.0


class TestAPI:
    """Tests for the FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "epidbot-openmaic-bridge"
