import logging

import httpx

logger = logging.getLogger(__name__)


class EpidBotAdapter:
    """
    HTTP client for EpidBot Chat API.
    Uses session-based chat to maintain context across requests.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._session_id: int | None = None
        logger.info(f"EpidBotAdapter initialized with base_url={self.base_url}")

    def _get_headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def create_session(self, name: str = "openmaic-bridge") -> int:
        """
        Create a new chat session.

        Args:
            name: Session name identifier

        Returns:
            Session ID
        """
        logger.info(f"Creating EpidBot session: {name}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/sessions",
                    json={"name": name},
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()
                self._session_id = result["id"]
                logger.info(f"EpidBot session created with id={self._session_id}")
                return self._session_id
        except Exception as e:
            logger.exception(f"Error creating EpidBot session: {e}")
            raise

    async def chat(self, message: str) -> str:
        """
        Send a chat message and get the response.

        Args:
            message: The message to send to EpidBot

        Returns:
            The response content from EpidBot
        """
        if self._session_id is None:
            raise RuntimeError("Session not created. Call create_session() first.")

        logger.info(f"Sending chat message to EpidBot session {self._session_id}")
        try:
            async with httpx.AsyncClient(timeout=600.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat",
                    json={
                        "message": message,
                        "session_id": self._session_id,
                    },
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()
                content = result.get("content", "")
                logger.info(f"EpidBot response received, length={len(content)}")
                return content
        except Exception as e:
            logger.exception(f"Error sending chat message: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if EpidBot server is healthy.

        Returns:
            True if healthy, raises exception otherwise
        """
        logger.debug(f"Checking EpidBot health at {self.base_url}/api/v1/health")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/health",
                    headers={"X-API-Key": self.api_key},
                )
                response.raise_for_status()
                logger.debug("EpidBot health check passed")
                return True
        except Exception as e:
            logger.error(f"EpidBot health check failed: {e}")
            raise
