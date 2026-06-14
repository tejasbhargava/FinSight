from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    NEWS_API_KEY: str

    MODEL_NAME: str = "openai/gpt-oss-20b:free"

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

    DATA_PATH: str = "data"
    FILINGS_PATH: str = "data/filings"
    INDEXES_PATH: str = "data/indexes"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()