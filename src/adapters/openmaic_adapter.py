import logging
from typing import AsyncGenerator

import httpx

logger = logging.getLogger(__name__)


class OpenMAICAdapter:
    """
    HTTP client for OpenMAIC API.

    Supports:
    - Classroom generation (async job)
    - Classroom storage (POST/GET /api/classroom)
    - Stateless chat with SSE streaming
    - Health checks
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip("/")
        logger.info(f"OpenMAICAdapter initialized with base_url={self.base_url}")

    async def generate_classroom(
        self,
        requirement: str,
        language: str = "pt-BR",
        enable_web_search: bool = False,
        enable_image_generation: bool = False,
        enable_video_generation: bool = False,
        enable_tts: bool = False,
        agent_mode: str | None = None,
        pdf_content: str | None = None,
    ) -> dict:
        """
        Submit classroom generation job to OpenMAIC.

        Args:
            requirement: The lesson requirement description
            language: Language code (e.g., "pt-BR", "en-US")
            enable_web_search: Whether to enable web search during generation
            enable_image_generation: Whether to enable AI image generation in scenes
            enable_video_generation: Whether to enable AI video generation in scenes
            enable_tts: Whether to enable text-to-speech for agents
            agent_mode: Agent mode (e.g., "teacher_only", "full_classroom")
            pdf_content: Optional PDF content to use as source material

        Returns:
            Response containing jobId for polling
        """
        logger.info(
            f"Submitting classroom generation to OpenMAIC: {self.base_url}/api/generate-classroom"
        )
        payload: dict = {
            "requirement": requirement,
            "language": language,
            "enableWebSearch": enable_web_search,
        }
        if enable_image_generation:
            payload["enableImageGeneration"] = True
        if enable_video_generation:
            payload["enableVideoGeneration"] = True
        if enable_tts:
            payload["enableTTS"] = True
        if agent_mode:
            payload["agentMode"] = agent_mode
        if pdf_content:
            payload["pdfContent"] = pdf_content

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate-classroom",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"OpenMAIC response: {result}")
                return result
        except Exception as e:
            logger.exception(f"Error calling OpenMAIC generate_classroom: {e}")
            raise

    async def poll_job(self, job_id: str) -> dict:
        """
        Check job status.

        Args:
            job_id: The job ID returned from generate_classroom

        Returns:
            Job status information
        """
        logger.debug(f"Polling job {job_id}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/generate-classroom/{job_id}"
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Job {job_id} status: {result.get('status', 'unknown')}")
                return result
        except Exception as e:
            logger.exception(f"Error polling job {job_id}: {e}")
            raise

    async def save_classroom(self, stage: dict, scenes: list) -> dict:
        """
        Save a generated classroom to persistent storage.

        Args:
            stage: The stage configuration (id, settings, etc.)
            scenes: List of generated scenes

        Returns:
            Response with classroom id and url
        """
        logger.info(f"Saving classroom to {self.base_url}/api/classroom")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/classroom",
                    json={"stage": stage, "scenes": scenes},
                )
                response.raise_for_status()
                result = response.json()
                logger.info(
                    f"Classroom saved: id={result.get('data', {}).get('id')}, "
                    f"url={result.get('data', {}).get('url')}"
                )
                return result
        except Exception as e:
            logger.exception(f"Error saving classroom: {e}")
            raise

    async def get_classroom(self, classroom_id: str) -> dict:
        """
        Retrieve generated classroom.

        Args:
            classroom_id: The classroom ID

        Returns:
            Classroom data
        """
        logger.info(f"Fetching classroom {classroom_id}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/classroom",
                    params={"id": classroom_id},
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Classroom {classroom_id} retrieved successfully")
                return result
        except Exception as e:
            logger.exception(f"Error getting classroom {classroom_id}: {e}")
            raise

    async def chat_stream(
        self,
        messages: list,
        store_state: dict,
        config: dict,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        provider_type: str | None = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Send a stateless chat message and receive SSE stream of events.

        Args:
            messages: List of chat messages (UIMessage format)
            store_state: Current store state {stage, scenes, currentSceneId, mode}
            config: Chat config {agentIds, sessionType?}
            api_key: Optional API key for LLM provider
            base_url: Optional base URL for LLM provider
            model: Optional model string
            provider_type: Optional provider type

        Yields:
            SSE events as dicts (type: text, tool_call, error, done, etc.)
        """
        logger.info(f"Starting chat stream with {len(messages)} messages")
        payload: dict = {
            "messages": messages,
            "storeState": store_state,
            "config": config,
        }
        if api_key:
            payload["apiKey"] = api_key
        if base_url:
            payload["baseUrl"] = base_url
        if model:
            payload["model"] = model
        if provider_type:
            payload["providerType"] = provider_type

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                    headers={"Accept": "text/event-stream"},
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            # Skip empty lines and comments (heartbeats)
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:]
                            import json

                            try:
                                event = json.loads(data_str)
                                logger.debug(f"SSE event: {event.get('type')}")
                                yield event
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse SSE event: {data_str}")
        except Exception as e:
            logger.exception(f"Error in chat stream: {e}")
            raise

    async def health_check(self) -> dict:
        """
        Check OpenMAIC server health.

        Returns:
            Health status information
        """
        logger.debug(f"Checking OpenMAIC health at {self.base_url}/api/health")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/health")
                response.raise_for_status()
                result = response.json()
                logger.debug(f"OpenMAIC health check passed")
                return result
        except Exception as e:
            logger.error(f"OpenMAIC health check failed: {e}")
            raise
