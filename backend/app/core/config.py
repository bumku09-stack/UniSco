from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "UniSco API"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/unisco"
    cors_origins: list[str] = ["http://localhost:3000"]

    # JWT — access token is short-lived and sent on every request; refresh
    # token is long-lived and only used to mint new access tokens.
    secret_key: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # Resend (transactional email for signup verification codes) — see
    # backend/README.md for why Resend over raw SMTP.
    resend_api_key: str = ""
    email_from: str = "UniSco <onboarding@resend.dev>"


settings = Settings()
