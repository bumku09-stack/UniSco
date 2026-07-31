from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)  # 인증용 — 로그인 ID로는 안 씀
    hashed_password: str
    is_verified: bool = Field(default=False)  # 이메일 인증 전에는 로그인 불가
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmailVerification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    code: str  # 6자리 숫자, 문자열로 저장(앞자리 0 보존)
    expires_at: datetime
    is_used: bool = Field(default=False)
    attempts: int = Field(default=0)  # 5회 틀리면 이 코드는 잠기고 재발송 필요
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
