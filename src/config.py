from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENMAIC_URL: str = "http://localhost:3000"
    EPIDBOT_URL: str = "https://api.epidbot.kwar-ai.com.br"
    EPIDBOT_API_KEY: str = ""
    PYSUS_DATA_PATH: str = "~/pysus"
    PYSUS_DOWNLOAD_TIMEOUT: int = 600
    PYSUS_FETCH_TIMEOUT: int = 300  # Timeout for fetching data from SINAN (seconds)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_DIR: str = "logs"
    LOG_FILE: str = "epidbot-openmaic.log"
    LOG_LEVEL: str = "INFO"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 5


settings = Settings()
