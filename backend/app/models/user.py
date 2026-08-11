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


class PasswordReset(SQLModel, table=True):
    """비밀번호 재설정 코드 — EmailVerification과 구조 동일(용도만 다름). 재사용 안 하고
    별도 테이블로 둔 이유: 이메일 인증(가입 완료용)과 비밀번호 재설정(이미 가입된 계정의
    보안 동작)은 성격이 달라서 섞이면 안 됨 — 코드 하나가 두 용도로 다 쓰일 수 있는
    구조가 되면 공격 표면이 넓어짐."""

    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    code: str
    expires_at: datetime
    is_used: bool = Field(default=False)
    attempts: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
