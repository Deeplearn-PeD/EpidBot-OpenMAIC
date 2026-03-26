import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.openmaic_adapter import OpenMAICAdapter
from src.config import settings
from src.generators.requirement_builder import RequirementBuilder
from src.models.schemas import (
    GenerateTrainingRequest,
    GenerateTrainingResponse,
    HealthResponse,
    JobStatusResponse,
    DataSummary,
)
from src.utils.data_fetcher import DengueDataFetcher

openmaic_adapter: OpenMAICAdapter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global openmaic_adapter
    openmaic_adapter = OpenMAICAdapter(base_url=settings.OPENMAIC_URL)
    yield


app = FastAPI(
    title="EpidBot-OpenMAIC Bridge",
    description="Generate epidemiological training content using real SINAN data and OpenMAIC",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    openmaic_connected = None
    if openmaic_adapter:
        try:
            await openmaic_adapter.health_check()
            openmaic_connected = True
        except Exception:
            openmaic_connected = False

    return HealthResponse(
        status="ok",
        service="epidbot-openmaic-bridge",
        openmaic_connected=openmaic_connected,
    )


@app.post("/api/generate-dengue-training", response_model=GenerateTrainingResponse)
async def generate_dengue_training(request: GenerateTrainingRequest):
    """
    Generate a dengue training classroom with real SINAN data.

    This endpoint:
    1. Fetches dengue surveillance data from SINAN via PySUS
    2. Summarizes the data into key statistics
    3. Builds a rich requirement string for OpenMAIC
    4. Submits the generation job to OpenMAIC
    5. Returns the job ID for polling
    """
    if not openmaic_adapter:
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        fetcher = DengueDataFetcher(cache_dir=settings.PYSUS_DATA_PATH)
        df = await fetcher.fetch_dengue_data(
            year=request.year,
            state=request.state,
            municipality_code=request.municipality_code,
        )

        summary = fetcher.summarize(df)

        if summary["total_cases"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No dengue data found for {request.region} in {request.year}",
            )

        builder = RequirementBuilder()
        requirement = builder.build_dengue_training(
            data_summary=summary,
            region=request.region,
            timeframe=f"Ano {request.year}",
            target_audience=request.target_audience,
            num_slides=request.num_slides,
            num_quizzes=request.num_quizzes,
        )

        result = await openmaic_adapter.generate_classroom(
            requirement=requirement,
            language=request.language,
        )

        job_id = result.get("jobId") or result.get("job_id")
        if not job_id:
            raise HTTPException(
                status_code=500,
                detail=f"OpenMAIC did not return a job ID: {result}",
            )

        return GenerateTrainingResponse(
            job_id=job_id,
            status="processing",
            data_summary=DataSummary(
                total_cases=summary["total_cases"],
                deaths=summary["deaths"],
                hospitalizations=summary["hospitalizations"],
                fatality_rate=summary["fatality_rate"],
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating training: {str(e)}")


@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Poll job status from OpenMAIC.

    Returns the current status of a classroom generation job.
    When status is 'completed', the classroom_url will be available.
    """
    if not openmaic_adapter:
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        result = await openmaic_adapter.poll_job(job_id)

        return JobStatusResponse(
            job_id=job_id,
            status=result.get("status", "unknown"),
            progress=result.get("progress"),
            classroom_url=result.get("classroomUrl") or result.get("classroom_url"),
            classroom_id=result.get("classroomId") or result.get("classroom_id"),
            error=result.get("error"),
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenMAIC error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error polling job: {str(e)}")


@app.get("/api/classroom/{classroom_id}")
async def get_classroom(classroom_id: str):
    """
    Retrieve a generated classroom from OpenMAIC.

    Returns the full classroom data including scenes, content, and agent configurations.
    """
    if not openmaic_adapter:
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        result = await openmaic_adapter.get_classroom(classroom_id)
        return result

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenMAIC error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting classroom: {str(e)}")


def run_server():
    """Run the FastAPI server using uvicorn."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )


if __name__ == "__main__":
    run_server()
