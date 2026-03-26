from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENMAIC_URL: str = "http://localhost:3000"
    PYSUS_DATA_PATH: str = "~/pysus"
    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings()
