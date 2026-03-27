import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


def setup_logging():
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / settings.LOG_FILE

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


setup_logging()
logger = logging.getLogger(__name__)


# Global exception handler for uncaught exceptions
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions before the program exits."""
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_uncaught_exception

openmaic_adapter: OpenMAICAdapter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global openmaic_adapter
    try:
        logger.info(
            f"Starting EpidBot-OpenMAIC Bridge service, connecting to OpenMAIC at {settings.OPENMAIC_URL}"
        )
        openmaic_adapter = OpenMAICAdapter(base_url=settings.OPENMAIC_URL)
        logger.info("OpenMAIC adapter initialized")
        yield
        logger.info("Shutting down EpidBot-OpenMAIC Bridge service")
    except Exception as e:
        logger.exception(f"Critical error in lifespan: {e}")
        raise


app = FastAPI(
    title="EpidBot-OpenMAIC Bridge",
    description="Generate epidemiological training content using real SINAN data and OpenMAIC",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for all unhandled exceptions."""
    logger.exception(f"Unhandled exception in request handler: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
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
    logger.info("Health check requested")
    openmaic_connected = None
    if openmaic_adapter:
        try:
            await openmaic_adapter.health_check()
            openmaic_connected = True
        except Exception as e:
            logger.error(f"OpenMAIC health check failed: {e}")
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
    logger.info(
        f"Generating dengue training for region={request.region}, year={request.year}, state={request.state}"
    )

    if not openmaic_adapter:
        logger.error("OpenMAIC adapter not initialized")
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        logger.info("Fetching dengue data from SINAN")
        logger.info(f"Fetch timeout set to {settings.PYSUS_FETCH_TIMEOUT} seconds")
        fetcher = DengueDataFetcher(cache_dir=settings.PYSUS_DATA_PATH)

        try:
            df = await asyncio.wait_for(
                fetcher.fetch_dengue_data(
                    year=request.year,
                    state=request.state,
                    municipality_code=request.municipality_code,
                ),
                timeout=settings.PYSUS_FETCH_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.error(
                f"Data fetch timed out after {settings.PYSUS_FETCH_TIMEOUT} seconds. "
                "Try using a municipality_code instead of state for faster results."
            )
            raise HTTPException(
                status_code=504,
                detail=f"Data fetch timed out after {settings.PYSUS_FETCH_TIMEOUT} seconds. "
                "The dataset may be too large. Try filtering by municipality_code.",
            )

        summary = fetcher.summarize(df)
        logger.info(f"Data summary: {summary['total_cases']} cases, {summary['deaths']} deaths")

        if summary["total_cases"] == 0:
            logger.warning(f"No dengue data found for {request.region} in {request.year}")
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

        logger.info("Submitting generation job to OpenMAIC")
        result = await openmaic_adapter.generate_classroom(
            requirement=requirement,
            language=request.language,
        )

        job_id = result.get("jobId") or result.get("job_id")
        if not job_id:
            logger.error(f"OpenMAIC did not return a job ID: {result}")
            raise HTTPException(
                status_code=500,
                detail=f"OpenMAIC did not return a job ID: {result}",
            )

        logger.info(f"Job created successfully: {job_id}")
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
        logger.exception(f"Error generating training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating training: {str(e)}")


@app.get("/api/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Poll job status from OpenMAIC.

    Returns the current status of a classroom generation job.
    When status is 'completed', the classroom_url will be available.
    """
    logger.info(f"Polling job status: {job_id}")

    if not openmaic_adapter:
        logger.error("OpenMAIC adapter not initialized")
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        result = await openmaic_adapter.poll_job(job_id)
        logger.info(f"Job {job_id} status: {result.get('status', 'unknown')}")

        return JobStatusResponse(
            job_id=job_id,
            status=result.get("status", "unknown"),
            progress=result.get("progress"),
            classroom_url=result.get("classroomUrl") or result.get("classroom_url"),
            classroom_id=result.get("classroomId") or result.get("classroom_id"),
            error=result.get("error"),
        )

    except httpx.HTTPStatusError as e:
        logger.error(
            f"OpenMAIC HTTP error for job {job_id}: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenMAIC error: {e.response.text}",
        )
    except Exception as e:
        logger.exception(f"Error polling job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error polling job: {str(e)}")


@app.get("/api/classroom/{classroom_id}")
async def get_classroom(classroom_id: str):
    """
    Retrieve a generated classroom from OpenMAIC.

    Returns the full classroom data including scenes, content, and agent configurations.
    """
    logger.info(f"Fetching classroom: {classroom_id}")

    if not openmaic_adapter:
        logger.error("OpenMAIC adapter not initialized")
        raise HTTPException(status_code=503, detail="OpenMAIC adapter not initialized")

    try:
        result = await openmaic_adapter.get_classroom(classroom_id)
        logger.info(f"Classroom {classroom_id} retrieved successfully")
        return result

    except httpx.HTTPStatusError as e:
        logger.error(
            f"OpenMAIC HTTP error for classroom {classroom_id}: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenMAIC error: {e.response.text}",
        )
    except Exception as e:
        logger.exception(f"Error getting classroom {classroom_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting classroom: {str(e)}")


def run_server():
    """Run the FastAPI server using uvicorn."""
    import signal
    import uvicorn

    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        logger.critical(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(f"Starting uvicorn server on {settings.HOST}:{settings.PORT}")

    try:
        uvicorn.run(
            "src.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level="info",
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    run_server()
