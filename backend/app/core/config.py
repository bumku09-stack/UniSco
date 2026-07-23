from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "UniSco API"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/unisco"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
