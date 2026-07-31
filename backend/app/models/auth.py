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


class RefreshRequest(BaseModel):
    refresh_token: str
