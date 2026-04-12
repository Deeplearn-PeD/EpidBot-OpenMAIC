"""Basic tests for EpidBot-OpenMAIC Bridge."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.generators.requirement_builder import RequirementBuilder
from src.utils.data_fetcher import DengueDataFetcher
from src.models.schemas import (
    GenerateTrainingRequest,
    SaveClassroomRequest,
    SaveClassroomResponse,
    JobStatusResponse,
)


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


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_generate_training_request_defaults(self):
        req = GenerateTrainingRequest(region="São Paulo")
        assert req.year == 2024
        assert req.language == "pt-BR"
        assert req.target_audience == "agentes de saúde"
        assert req.num_slides == 8
        assert req.num_quizzes == 3
        assert req.enable_web_search is False
        assert req.enable_image_generation is False
        assert req.enable_tts is False
        assert req.agent_mode is None
        assert req.pdf_content is None

    def test_generate_training_request_with_options(self):
        req = GenerateTrainingRequest(
            region="Rio",
            year=2023,
            language="en-US",
            enable_web_search=True,
            enable_image_generation=True,
            enable_tts=True,
            agent_mode="teacher_only",
        )
        assert req.enable_web_search is True
        assert req.enable_image_generation is True
        assert req.enable_tts is True
        assert req.agent_mode == "teacher_only"

    def test_save_classroom_request(self):
        req = SaveClassroomRequest(
            stage={"id": "test-stage", "agents": ["teacher"]},
            scenes=[{"id": "scene1", "content": "Test"}],
        )
        assert req.stage["id"] == "test-stage"
        assert len(req.scenes) == 1

    def test_save_classroom_response(self):
        resp = SaveClassroomResponse(
            id="classroom-123",
            url="http://localhost:3000/classroom/classroom-123",
        )
        assert resp.id == "classroom-123"
        assert "http://" in resp.url

    def test_job_status_response_with_new_fields(self):
        resp = JobStatusResponse(
            job_id="job-1",
            status="completed",
            progress=100.0,
            scenes_generated=10,
            done=True,
        )
        assert resp.scenes_generated == 10
        assert resp.done is True


class TestNewEndpoints:
    """Tests for new OpenMAIC integration endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_save_classroom_endpoint_structure(self, client):
        """Test that the save-classroom endpoint accepts valid requests."""
        # Mock the adapter
        with patch("src.main.openmaic_adapter") as mock_adapter:
            mock_adapter.save_classroom = AsyncMock(
                return_value={
                    "data": {
                        "id": "test-classroom",
                        "url": "http://localhost:3000/classroom/test-classroom",
                    }
                }
            )

            response = client.post(
                "/api/save-classroom",
                json={
                    "stage": {"id": "stage-1", "title": "Test"},
                    "scenes": [{"id": "s1", "type": "slide"}],
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-classroom"
            assert "classroom" in data["url"]

    def test_save_classroom_without_adapter(self, client):
        """Test that save-classroom returns 503 when adapter is not initialized."""
        with patch("src.main.openmaic_adapter", None):
            response = client.post(
                "/api/save-classroom",
                json={
                    "stage": {"id": "stage-1"},
                    "scenes": [],
                },
            )
            assert response.status_code == 503
