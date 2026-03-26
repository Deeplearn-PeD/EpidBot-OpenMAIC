from pydantic import BaseModel, Field


class GenerateTrainingRequest(BaseModel):
    """Request model for generating dengue training content."""

    region: str = Field(
        ...,
        description="Region name (e.g., 'São Paulo', 'Brasil')",
        examples=["São Paulo"],
    )
    year: int = Field(
        default=2024,
        description="Year to fetch data for",
        ge=2010,
        le=2030,
    )
    municipality_code: str | None = Field(
        default=None,
        description="IBGE municipality code for filtering",
    )
    state: str | None = Field(
        default=None,
        description="State abbreviation (e.g., 'SP', 'RJ')",
    )
    language: str = Field(
        default="pt-BR",
        description="Language code for content generation",
    )
    target_audience: str = Field(
        default="agentes de saúde",
        description="Target audience for the training",
    )
    num_slides: int = Field(
        default=8,
        description="Target number of slides",
        ge=5,
        le=20,
    )
    num_quizzes: int = Field(
        default=3,
        description="Target number of quiz questions",
        ge=1,
        le=10,
    )


class DataSummary(BaseModel):
    """Summary of epidemiological data."""

    total_cases: int
    deaths: int
    hospitalizations: int
    fatality_rate: float


class GenerateTrainingResponse(BaseModel):
    """Response model for training generation request."""

    job_id: str
    status: str
    data_summary: DataSummary


class JobStatusResponse(BaseModel):
    """Response model for job status polling."""

    job_id: str
    status: str
    progress: float | None = None
    classroom_url: str | None = None
    classroom_id: str | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    service: str
    openmaic_connected: bool | None = None
