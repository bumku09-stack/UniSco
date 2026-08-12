from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr


class SignupResponse(BaseModel):
    message: str = "인증 코드를 이메일로 보냈습니다."


class VerifyCodeRequest(BaseModel):
    identifier: str  # username 또는 email
    code: str = Field(min_length=6, max_length=6)


class ResendCodeRequest(BaseModel):
    identifier: str  # username 또는 email


class LoginRequest(BaseModel):
    username: str
    password: str


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


class DeleteAccountRequest(BaseModel):
    # 세션이 탈취됐거나 다른 사람이 로그인된 기기를 만졌을 때 실수로/악의적으로 계정을
    # 지우는 걸 막기 위해 비밀번호 재확인을 받음 — 되돌릴 수 없는 작업이라 로그인
    # 상태(토큰)만으로는 부족하다고 판단함.
    password: str
