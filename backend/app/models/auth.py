import re

from pydantic import BaseModel, EmailStr, Field, field_validator

# 영문/숫자/특수문자를 각각 최소 1개씩 포함해야 함(2026-08-21 추가 — 이전엔 길이 제한만
# 있어서 "aaaaaaaa" 같은 비밀번호도 통과됐음). SignupRequest.password와
# ResetPasswordRequest.new_password가 이 규칙을 공유함.
_PASSWORD_COMPLEXITY_PATTERN = re.compile(r"(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9])")


def _validate_password_complexity(value: str) -> str:
    if not _PASSWORD_COMPLEXITY_PATTERN.search(value):
        raise ValueError("비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 합니다.")
    return value


class SignupRequest(BaseModel):
    username: str = Field(min_length=5, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr

    _validate_password = field_validator("password")(_validate_password_complexity)


class SignupResponse(BaseModel):
    message: str = "인증 코드를 이메일로 보냈습니다."


# GET /auth/check-username 응답(2026-08-21 추가) — 회원가입 제출 전에 아이디 중복을 미리
# 확인하는 용도. 최종 방어선은 여전히 signup()의 409 에러(레이스 컨디션 등으로 확인 이후
# 실제 제출 사이에 다른 사람이 같은 아이디를 선점했을 수 있음)라 이 응답만 믿고 signup()의
# 중복 체크를 지우면 안 됨.
class UsernameAvailabilityResponse(BaseModel):
    available: bool


class VerifyCodeRequest(BaseModel):
    identifier: str  # username 또는 email
    code: str = Field(min_length=6, max_length=6)


class ResendCodeRequest(BaseModel):
    identifier: str  # username 또는 email


class LoginRequest(BaseModel):
    username: str
    password: str


class KakaoLoginRequest(BaseModel):
    code: str  # 카카오가 콜백 URL에 붙여준 인가 코드(one-time, 짧은 유효시간)
    # 2026-08-13 추가 — 프론트가 인가 요청 때 실제로 보낸 redirect_uri를 그대로 넘겨받음.
    # 카카오는 토큰 교환 시 이 값이 인가 요청 때와 정확히 일치해야만 허용하는데, 배포
    # 도메인이 여러 개(예: unisco-pi.vercel.app, www.unisco.co.kr)라 백엔드가 고정값 하나만
    # 갖고 있으면 다른 도메인에서 로그인한 사람은 항상 mismatch로 실패함 — 그래서 백엔드가
    # 추측하지 않고 프론트가 실제로 쓴 값을 그대로 전달받아 씀(core/kakao.py 참고).
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    # 로그인 직후 프론트가 /users/me/spec-status를 또 호출하지 않도록 여기 같이 실어보냄
    # (로그인 응답 시점 기준 값 — refresh에서도 채우지만 보통 이미 로그인된 상태라 안 씀).
    spec_completed: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    identifier: str  # username 또는 email


class ForgotPasswordResponse(BaseModel):
    message: str = "비밀번호 재설정 코드를 이메일로 보냈습니다."


class ResetPasswordRequest(BaseModel):
    identifier: str
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)

    _validate_new_password = field_validator("new_password")(_validate_password_complexity)


class DeleteAccountRequest(BaseModel):
    # 세션이 탈취됐거나 다른 사람이 로그인된 기기를 만졌을 때 실수로/악의적으로 계정을
    # 지우는 걸 막기 위해 비밀번호 재확인을 받음 — 되돌릴 수 없는 작업이라 로그인
    # 상태(토큰)만으로는 부족하다고 판단함.
    password: str
