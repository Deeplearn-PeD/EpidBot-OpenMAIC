import logging

import httpx

logger = logging.getLogger(__name__)


class OpenMAICAdapter:
    """
    HTTP client for OpenMAIC API.
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip("/")
        logger.info(f"OpenMAICAdapter initialized with base_url={self.base_url}")

    async def generate_classroom(
        self,
        requirement: str,
        language: str = "pt-BR",
        enable_web_search: bool = False,
    ) -> dict:
        """
        Submit classroom generation job to OpenMAIC.

        Args:
            requirement: The lesson requirement description
            language: Language code (e.g., "pt-BR", "en-US")
            enable_web_search: Whether to enable web search during generation

        Returns:
            Response containing jobId for polling
        """
        logger.info(
            f"Submitting classroom generation to OpenMAIC: {self.base_url}/api/generate-classroom"
        )
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate-classroom",
                    json={
                        "requirement": requirement,
                        "language": language,
                        "enableWebSearch": enable_web_search,
                    },
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
                response = await client.get(f"{self.base_url}/api/generate-classroom/{job_id}")
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Job {job_id} status: {result.get('status', 'unknown')}")
                return result
        except Exception as e:
            logger.exception(f"Error polling job {job_id}: {e}")
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
