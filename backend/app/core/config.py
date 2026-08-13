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

    # 카카오 로그인 (2026-08-13 추가). client_id는 카카오 디벨로퍼스의 REST API 키 — 프론트에도
    # 노출되는 값(NEXT_PUBLIC_KAKAO_CLIENT_ID)이라 비밀값 아님. client_secret은 카카오 앱
    # 설정에서 "Client Secret" 기능을 켰을 때만 필요(안 켰으면 빈 문자열로 둬도 됨, 코드 교환
    # 요청에서 그 필드 자체를 생략함 — core/kakao.py 참고). redirect_uri는 여기 고정값으로
    # 안 두고 매 요청마다 프론트가 실제로 쓴 값을 그대로 받음(배포 도메인이 여러 개일 수
    # 있어서 — KakaoLoginRequest.redirect_uri 참고).
    kakao_client_id: str = ""
    kakao_client_secret: str = ""


settings = Settings()
