from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(unique=True, index=True)
    # 2026-08-13 카카오 로그인 추가 전까지는 NOT NULL이었음 — 소셜 전용 계정은 카카오가
    # 이메일 동의를 안 줬을 수 있어서 nullable로 변경. Postgres UNIQUE 컬럼은 NULL을
    # 여러 개 허용하므로(NULL끼리는 서로 다른 값으로 취급) 소셜 유저 여럿이 email=None이어도
    # 유니크 제약과 충돌 안 함.
    email: str | None = Field(default=None, unique=True, index=True)  # 인증용 — 로그인 ID로는 안 씀
    # 2026-08-13 — 카카오 등 소셜 전용 계정은 비밀번호 자체가 없음(None). core/security.py의
    # verify_password()를 그런 계정에 쓰면 안 되므로, api/auth.py의 login()에서 반드시
    # None 체크를 먼저 함.
    hashed_password: str | None = None
    # 이메일 인증 전에는 로그인 불가. 소셜 로그인(카카오 등)은 가입 시 바로 True로 채워짐 —
    # 카카오가 이미 신원을 확인한 셈이라 우리 쪽 이메일 OTP가 별도로 필요 없음.
    is_verified: bool = Field(default=False)
    # 2026-08-13 카카오 로그인 추가 — 카카오의 회원번호(문자열로 저장, 카카오 응답 자체가
    # 문자열이 아니라 숫자지만 향후 다른 소셜 제공자 id와 타입을 맞추기 위해 str로 통일).
    # None=이 계정은 카카오로 로그인한 적 없음(또는 아직 연결 안 됨).
    kakao_id: str | None = Field(default=None, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PendingSignup(SQLModel, table=True):
    """인증 코드를 확인하기 전까지는 User 테이블에 아무것도 안 만들고, 여기 임시로만
    보관함(2026-08-21 추가) — 예전엔 가입 버튼 누르는 순간 바로 User를 만들어서, 오타/존재
    하지 않는 이메일로 시도한 계정이 인증 안 된 채로 아이디/이메일을 점유해버리는 문제가
    있었음(ghost_accounts.py의 시간 기반 청소는 그 증상을 완화만 함, 근본 원인은 "아직
    확정 안 된 걸 미리 저장하는 것"이었음). 이 테이블은 username/email에 유니크 제약이
    없음 — 어차피 진짜 계정이 아니라서 여러 개 겹쳐도 무해하고, 인증 코드를 맞게 입력한
    사람만 이 정보로 User를 실제로 생성함(api/auth.py의 verify_code 참고)."""

    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str
    code: str
    expires_at: datetime
    attempts: int = Field(default=0)
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
