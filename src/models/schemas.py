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
    enable_web_search: bool = Field(
        default=False,
        description="Enable web search during generation",
    )
    enable_image_generation: bool = Field(
        default=False,
        description="Enable AI image generation in scenes",
    )
    enable_video_generation: bool = Field(
        default=False,
        description="Enable AI video generation in scenes",
    )
    enable_tts: bool = Field(
        default=False,
        description="Enable text-to-speech for agents",
    )
    agent_mode: str | None = Field(
        default=None,
        description="Agent mode (e.g., 'teacher_only', 'full_classroom')",
    )
    pdf_content: str | None = Field(
        default=None,
        description="Optional PDF content to use as source material",
    )


class EnhancedTrainingRequest(GenerateTrainingRequest):
    """Extended request model with OpenMAIC advanced features."""

    pass  # Inherits all fields from GenerateTrainingRequest


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
    scenes_generated: int | None = None
    done: bool | None = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    service: str
    openmaic_connected: bool | None = None
    epidbot_connected: bool | None = None


class SaveClassroomRequest(BaseModel):
    """Request model for saving a classroom."""

    stage: dict = Field(
        ...,
        description="Stage configuration (id, settings, agents, etc.)",
    )
    scenes: list = Field(
        ...,
        description="List of generated scenes",
    )


class SaveClassroomResponse(BaseModel):
    """Response model for saving a classroom."""

    id: str
    url: str


class ChatStreamRequest(BaseModel):
    """Request model for stateless chat with SSE streaming."""

    messages: list = Field(
        ...,
        description="List of chat messages in UIMessage format",
    )
    store_state: dict = Field(
        ...,
        description="Current store state {stage, scenes, currentSceneId, mode}",
    )
    config: dict = Field(
        ...,
        description="Chat config {agentIds, sessionType?}",
    )
    api_key: str | None = Field(
        default=None,
        description="Optional API key for LLM provider",
    )
    base_url_provider: str | None = Field(
        default=None,
        description="Optional base URL for LLM provider",
    )
    model: str | None = Field(
        default=None,
        description="Optional model string",
    )
    provider_type: str | None = Field(
        default=None,
        description="Optional provider type",
    )
